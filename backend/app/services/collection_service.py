from __future__ import annotations

import hashlib
import json
import logging
import re
import time
import unicodedata
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import urldefrag, urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser

import httpx
from app.services.ingestion_service import validate_documents

logger = logging.getLogger("temple_heritage.collection")
USER_AGENT = "TempleHeritageInformationAssistant/1.0 (respectful public-page collector)"
SKIP_TAGS = {"script", "style", "noscript", "svg", "nav", "header", "footer", "aside", "form", "button", "iframe"}
MAX_BODY_BYTES = 2_000_000


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _event(level: int, event: str, **fields: Any) -> None:
    logger.log(level, json.dumps({"event": event, **fields}, ensure_ascii=False, sort_keys=True))


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    return re.sub(r"\s+", " ", value).strip()


def canonical_url(url: str) -> str:
    clean, _fragment = urldefrag(url.strip())
    parts = urlparse(clean)
    if parts.scheme.lower() != "https" or not parts.hostname:
        raise ValueError("source URLs must use HTTPS and include a host")
    if parts.username or parts.password or parts.port not in (None, 443):
        raise ValueError("source URLs must not include credentials or a non-standard port")
    path = re.sub(r"/{2,}", "/", parts.path or "/")
    return urlunparse(("https", parts.netloc.lower(), path, "", parts.query, ""))


def stable_id(value: str, prefix: str = "collected") -> str:
    return f"{prefix}_{hashlib.sha256(value.encode('utf-8')).hexdigest()[:24]}"


def _page_hash(documents: list[dict[str, Any]]) -> str:
    fingerprint = [
        {field: document.get(field) for field in ("document_id", "content_hash", "source_title", "publication_date", "language")}
        for document in documents
    ]
    return hashlib.sha256(json.dumps(fingerprint, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


class _PageParser(HTMLParser):
    """Small, dependency-free parser for visible page text and source metadata."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.title_depth = 0
        self.heading_depth = 0
        self.title_parts: list[str] = []
        self.heading_parts: list[str] = []
        self.text_parts: list[str] = []
        self.language: Optional[str] = None
        self.canonical: Optional[str] = None
        self.published: Optional[str] = None
        self.table_rows: list[list[str]] = []
        self._row: Optional[list[str]] = None
        self._cell: Optional[list[str]] = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attrs_map = dict(attrs)
        if tag == "html":
            self.language = attrs_map.get("lang")
        elif tag == "meta":
            name = (attrs_map.get("name") or attrs_map.get("property") or "").casefold()
            if name in {"article:published_time", "date", "dcterms.created", "pubdate"}:
                self.published = attrs_map.get("content")
        elif tag == "link" and "canonical" in (attrs_map.get("rel") or "").casefold().split():
            self.canonical = attrs_map.get("href")
        elif tag == "title":
            self.title_depth += 1
        elif re.fullmatch(r"h[1-6]", tag):
            self.heading_depth += 1
        elif tag == "tr":
            self._row = []
        elif tag in {"td", "th"} and self._row is not None:
            self._cell = []
        if tag in SKIP_TAGS:
            self.skip_depth += 1
        elif tag in {"p", "br", "div", "li", "tr", "section", "article", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.text_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
        if tag == "title" and self.title_depth:
            self.title_depth -= 1
        if re.fullmatch(r"h[1-6]", tag) and self.heading_depth:
            self.heading_depth -= 1
            self.text_parts.append("\n")
        if tag in {"td", "th"} and self._cell is not None and self._row is not None:
            self._row.append(normalize_text(" ".join(self._cell)))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if any(self._row):
                self.table_rows.append(self._row)
            self._row = None
        elif tag in {"p", "br", "div", "li", "section", "article"}:
            self.text_parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_parts.append(data)
        if self.skip_depth:
            return
        if self.heading_depth:
            self.heading_parts.append(data)
        self.text_parts.append(data)
        if self._cell is not None:
            self._cell.append(data)

    @property
    def title(self) -> str:
        return normalize_text(" ".join(self.title_parts))

    @property
    def text(self) -> str:
        lines = [normalize_text(line) for line in "".join(self.text_parts).splitlines()]
        return "\n".join(line for line in lines if line)


def _read_json(path: Path, default: Any) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return default


def atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _host_allowed(url: str, source: dict[str, Any]) -> bool:
    host = (urlparse(url).hostname or "").lower()
    allowed = {str(item).lower() for item in source.get("allowed_hosts", [])}
    return bool(host and host in allowed)


def _match_catalogue_temple(title: str, text: str, catalogue: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
    normalized = re.sub(r"[^a-z0-9]+", " ", f"{title} {text[:5000]}".casefold()).strip()
    matches: list[dict[str, Any]] = []
    for temple in catalogue:
        aliases = temple.get("names", [])
        for alias in aliases if isinstance(aliases, list) else []:
            candidate = re.sub(r"[^a-z0-9]+", " ", str(alias).casefold()).strip()
            if len(candidate) > 5 and re.search(rf"\b{re.escape(candidate)}\b", normalized):
                matches.append(temple)
                break
    unique = {item.get("id"): item for item in matches}
    return next(iter(unique.values())) if len(unique) == 1 else None


def _extract_page_documents(
    source: dict[str, Any], requested_url: str, response: httpx.Response,
    catalogue: list[dict[str, Any]], retrieval_date: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().casefold()
    if content_type not in {"text/html", "application/xhtml+xml"}:
        raise ValueError(f"unsupported content type: {content_type or 'missing'}")
    if len(response.content) > MAX_BODY_BYTES:
        raise ValueError("response exceeds configured size limit")
    parser = _PageParser()
    parser.feed(response.text)
    title = parser.title or requested_url
    text = parser.text
    canonical = urljoin(requested_url, parser.canonical) if parser.canonical else requested_url
    if not _host_allowed(canonical, source):
        canonical = requested_url
    canonical = canonical_url(canonical)
    documents: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []

    temple = _match_catalogue_temple(title, text, catalogue)
    rows = parser.table_rows
    if source.get("parser") == "tn_arch_temple_table":
        header_index = next((i for i, row in enumerate(rows) if {x.casefold() for x in row} >= {"name of the temples", "taluk", "district"}), None)
        if header_index is not None:
            headers = [x.casefold() for x in rows[header_index]]
            name_i, taluk_i, district_i = headers.index("name of the temples"), headers.index("taluk"), headers.index("district")
            for row in rows[header_index + 1:]:
                if max(name_i, taluk_i, district_i) >= len(row):
                    continue
                name, taluk, district = row[name_i], row[taluk_i], row[district_i]
                if not name:
                    continue
                # This document is an attributed transcription of one table row,
                # not an inferred description or generated historical summary.
                row_text = normalize_text(f"Temple listed: {name}. Taluk listed: {taluk or 'not stated'}. District listed: {district or 'not stated'}.")
                matched = _match_catalogue_temple(name, name, catalogue)
                document = _make_document(
                    source, canonical, title, row_text, retrieval_date, parser,
                    matched, topic="temple_listing", row_key=name,
                    extra={"taluk": taluk or None, "district": district or None, "extracted_name": name, "extraction_status": "needs_review"},
                )
                documents.append(document)
                if not matched:
                    candidates.append({
                        "candidate_id": stable_id(f"{canonical}|{name.casefold()}", "candidate"),
                        "names": [name], "state": source.get("state_context"), "district": district or None,
                        "taluk": taluk or None, "description": None,
                        "source_title": title, "source_url": canonical,
                        "verification_status": "needs_review",
                    })
            if documents:
                return documents, candidates

    if len(text) < 80:
        raise ValueError("page did not contain enough visible text to create a knowledge document")
    document = _make_document(source, canonical, title, text, retrieval_date, parser, temple)
    documents.append(document)
    if not temple and source.get("record_type") == "temple_page":
        candidates.append({
            "candidate_id": stable_id(canonical, "candidate"),
            "names": [title] if title and title != requested_url else [],
            "state": None, "district": None, "taluk": None, "description": None,
            "source_title": title, "source_url": canonical,
            "verification_status": "needs_review",
        })
    return documents, candidates


def _make_document(
    source: dict[str, Any], source_url: str, title: str, text: str,
    retrieval_date: str, parser: _PageParser, temple: Optional[dict[str, Any]],
    topic: str = "general_heritage", row_key: str = "",
    extra: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    identity = f"{source_url}|{row_key.casefold()}" if row_key else source_url
    cleaned = normalize_text(text)
    normalized = re.sub(r"[^a-z0-9]+", " ", cleaned.casefold())
    if re.search(r"\b(inscription|epigraph|stone record)\w*\b", normalized):
        topic = "inscriptions"
    elif re.search(r"\b(architecture|sculpt|gopuram|vimana|spire|pillar)\w*\b", normalized):
        topic = "architecture"
    elif re.search(r"\b(festival|rath yatra|procession|celebration)\w*\b", normalized):
        topic = "festivals_and_rituals"
    elif re.search(r"\b(history|built|century|dynasty|king|date)\w*\b", normalized):
        topic = "history"
    result: dict[str, Any] = {
        "document_id": stable_id(identity),
        "temple_id": temple.get("id") if temple else None,
        "temple_name": (temple.get("names") or [None])[0] if temple else (extra or {}).get("extracted_name"),
        "state": temple.get("state") if temple else source.get("state_context"),
        "district": temple.get("district") if temple else (extra or {}).get("taluk_district"),
        "topic": topic,
        "source_title": title,
        "source_url": source_url,
        "publisher": source["name"],
        "language": (parser.language or "und").split("-", 1)[0].lower(),
        "publication_date": parser.published,
        "retrieval_date": retrieval_date,
        "collection_timestamp": retrieval_date,
        "source_type": source.get("category"),
        "verification_status": "source_attributed_needs_review",
        "content_hash": hashlib.sha256(cleaned.encode("utf-8")).hexdigest(),
        "text": cleaned,
    }
    if extra:
        result.update(extra)
    return result


class CollectionEngine:
    """Collect only explicit, allowlisted public HTML pages under robots policy."""

    def __init__(
        self,
        registry_path: Path,
        collected_path: Path,
        state_path: Path,
        catalogue_path: Path,
        *,
        client: Optional[httpx.Client] = None,
        timeout: float = 12.0,
        retries: int = 2,
        backoff_seconds: float = 0.5,
        min_domain_interval: float = 1.0,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.registry_path = registry_path
        self.collected_path = collected_path
        self.state_path = state_path
        self.catalogue_path = catalogue_path
        self.client = client or httpx.Client(timeout=timeout, follow_redirects=False, headers={"User-Agent": USER_AGENT})
        self.timeout = timeout
        self.retries = retries
        self.backoff_seconds = backoff_seconds
        self.min_domain_interval = min_domain_interval
        self.sleeper = sleeper
        self._last_request: dict[str, float] = {}
        self._domain_intervals: dict[str, float] = {}
        self._robots: dict[str, Optional[RobotFileParser]] = {}
        self._sitemaps: dict[str, list[str]] = {}

    def close(self) -> None:
        self.client.close()

    def _request(self, url: str, headers: Optional[dict[str, str]] = None) -> httpx.Response:
        host = (urlparse(url).hostname or "").lower()
        previous = self._last_request.get(host)
        if previous is not None:
            wait = self._domain_intervals.get(host, self.min_domain_interval) - (time.monotonic() - previous)
            if wait > 0:
                self.sleeper(wait)
        last_error: Optional[Exception] = None
        for attempt in range(self.retries + 1):
            try:
                self._last_request[host] = time.monotonic()
                with self.client.stream("GET", url, headers=headers or {}, timeout=self.timeout) as response:
                    declared_length = response.headers.get("content-length")
                    if declared_length and declared_length.isdigit() and int(declared_length) > MAX_BODY_BYTES:
                        raise ValueError("response exceeds configured size limit")
                    body = bytearray()
                    for block in response.iter_bytes():
                        body.extend(block)
                        if len(body) > MAX_BODY_BYTES:
                            raise ValueError("response exceeds configured size limit")
                    response._content = bytes(body)
                if response.status_code == 429 or 500 <= response.status_code < 600:
                    if attempt < self.retries:
                        retry_after = response.headers.get("retry-after")
                        delay = float(retry_after) if retry_after and retry_after.isdigit() else self.backoff_seconds * (2 ** attempt)
                        self.sleeper(delay)
                        continue
                return response
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt < self.retries:
                    self.sleeper(self.backoff_seconds * (2 ** attempt))
        if last_error:
            raise last_error
        raise RuntimeError("request retry loop ended unexpectedly")

    def _robots_for(self, source: dict[str, Any], url: str) -> Optional[RobotFileParser]:
        host = urlparse(url).hostname or ""
        if host in self._robots:
            return self._robots[host]
        robots_url = f"{urlparse(url).scheme}://{host}/robots.txt"
        try:
            response = self._request(robots_url)
            if response.status_code in {404, 410}:
                parser = RobotFileParser(robots_url)
                parser.parse([])
                self._sitemaps[host] = []
            elif response.status_code == 200 and response.headers.get("content-type", "").startswith(("text/plain", "application/octet-stream")):
                parser = RobotFileParser(robots_url)
                lines = response.text.splitlines()
                parser.parse(lines)
                self._sitemaps[host] = [line.split(":", 1)[1].strip() for line in lines if line.strip().casefold().startswith("sitemap:")]
            else:
                _event(logging.WARNING, "robots_check_failed", host=host, status_code=response.status_code)
                parser = None
        except Exception as exc:
            _event(logging.WARNING, "robots_check_error", host=host, error_type=type(exc).__name__, message=str(exc))
            parser = None
            self._sitemaps[host] = []
        if parser is not None:
            try:
                crawl_delay = parser.crawl_delay(USER_AGENT) or parser.crawl_delay("*")
                if crawl_delay is not None:
                    self._domain_intervals[host] = max(self.min_domain_interval, float(crawl_delay))
            except (TypeError, ValueError):
                pass
        self._robots[host] = parser
        return parser

    def _permitted(self, source: dict[str, Any], url: str) -> tuple[bool, str]:
        try:
            url = canonical_url(url)
        except ValueError as exc:
            return False, str(exc)
        if not _host_allowed(url, source):
            return False, "host is not allowlisted for this source"
        parser = self._robots_for(source, url)
        if parser is None:
            return False, "robots.txt could not be checked"
        if not parser.can_fetch(USER_AGENT, url):
            return False, "robots.txt disallows this URL"
        return True, ""

    def _source_urls(self, source: dict[str, Any]) -> list[str]:
        urls = list(source.get("start_urls", []))
        sitemap_urls = list(source.get("sitemap_urls", []))
        if source.get("use_robots_sitemaps"):
            for host in source.get("allowed_hosts", []):
                self._robots_for(source, f"https://{host}/")
                sitemap_urls.extend(self._sitemaps.get(host, []))
        prefixes = tuple(source.get("sitemap_path_prefixes", []))
        maximum = int(source.get("max_pages", 20))
        discovered: list[str] = []
        for sitemap_url in dict.fromkeys(sitemap_urls):
            allowed, reason = self._permitted(source, str(sitemap_url))
            if not allowed:
                _event(logging.WARNING, "sitemap_skipped", source_id=source.get("id"), url=sitemap_url, reason=reason)
                continue
            try:
                response = self._request(str(sitemap_url), {"Accept": "application/xml,text/xml;q=0.9"})
                if response.status_code != 200 or len(response.content) > MAX_BODY_BYTES:
                    raise ValueError(f"sitemap returned HTTP {response.status_code} or exceeded size limit")
                if response.headers.get("content-type", "").split(";", 1)[0].strip().casefold() not in {"application/xml", "text/xml", "application/octet-stream"}:
                    raise ValueError("unsupported sitemap content type")
                root = ET.fromstring(response.content)
                for element in root.iter():
                    if element.tag.rsplit("}", 1)[-1] != "loc" or not element.text:
                        continue
                    candidate = canonical_url(urljoin(str(sitemap_url), element.text.strip()))
                    if _host_allowed(candidate, source) and prefixes and urlparse(candidate).path.startswith(prefixes):
                        discovered.append(candidate)
                        if len(discovered) >= maximum:
                            break
            except Exception as exc:
                _event(logging.WARNING, "sitemap_failed", source_id=source.get("id"), url=sitemap_url, error_type=type(exc).__name__, message=str(exc))
        return list(dict.fromkeys(urls + discovered))[:maximum]

    def collect(self, source_id: Optional[str] = None, dry_run: bool = False) -> dict[str, Any]:
        registry = _read_json(self.registry_path, {"version": 1, "sources": []})
        if not isinstance(registry, dict) or not isinstance(registry.get("sources"), list):
            raise ValueError("source registry must be a JSON object containing a sources array")
        if any(not isinstance(source, dict) or not source.get("id") or not isinstance(source.get("allowed_hosts"), list) or not isinstance(source.get("start_urls"), list) or not source.get("permitted_collection_method") for source in registry["sources"]):
            raise ValueError("each source registry entry needs an id, allowlist, start URLs, and collection method")
        state = _read_json(self.state_path, {"pages": {}})
        pages = state.get("pages", {}) if isinstance(state, dict) else {}
        existing_collected = _read_json(self.collected_path, [])
        if not isinstance(existing_collected, list):
            existing_collected = []
        catalogue = _read_json(self.catalogue_path, [])
        if not isinstance(catalogue, list):
            catalogue = []
        existing_by_url: dict[str, list[dict[str, Any]]] = {}
        for doc in existing_collected:
            if isinstance(doc, dict) and isinstance(doc.get("source_url"), str):
                existing_by_url.setdefault(doc["source_url"], []).append(doc)
        page_documents: dict[str, list[dict[str, Any]]] = dict(existing_by_url)

        counts = {"attempted": 0, "succeeded": 0, "failed": 0, "skipped": 0, "new": 0, "updated": 0, "unchanged": 0, "duplicates": 0, "skipped_documents": 0}
        source_results: list[dict[str, Any]] = []
        new_pages: dict[str, dict[str, Any]] = dict(pages)
        if not dry_run:
            registry["sources"] = [dict(s) for s in registry["sources"]]
        selected_sources = [s for s in registry["sources"] if not source_id or s.get("id") == source_id]
        if source_id and not selected_sources:
            raise ValueError(f"source id not found in registry: {source_id}")
        seen_page_hashes: dict[str, str] = {}

        for source in selected_sources:
            source_id_value = str(source.get("id", "unknown"))
            if source.get("permitted_collection_method") not in {
                "explicit_public_html_robots_checked",
                "public_html_only_after_terms_and_robots_review",
            } or source.get("parser", "generic_html") not in {"generic_html", "tn_arch_temple_table"}:
                skipped_urls = len(source.get("start_urls", []))
                counts["skipped"] += skipped_urls
                source_results.append({"source_id": source_id_value, "status": "unsupported_method", "succeeded": 0, "failed": 0, "skipped": skipped_urls})
                _event(logging.WARNING, "unsupported_source_method", source_id=source_id_value)
                continue
            if not source.get("enabled", False):
                counts["skipped"] += len(source.get("start_urls", []))
                source_results.append({"source_id": source_id_value, "status": "disabled", "succeeded": 0, "failed": 0, "skipped": len(source.get("start_urls", []))})
                continue
            if source.get("terms_review_status") != "approved":
                counts["skipped"] += len(source.get("start_urls", []))
                _event(logging.WARNING, "source_policy_review_required", source_id=source_id_value)
                source_results.append({"source_id": source_id_value, "status": "terms_review_required", "succeeded": 0, "failed": 0, "skipped": len(source.get("start_urls", []))})
                continue
            successful_for_source = 0
            failed_for_source = 0
            skipped_for_source = 0
            for raw_url in self._source_urls(source):
                counts["attempted"] += 1
                try:
                    url = canonical_url(str(raw_url))
                except ValueError as exc:
                    counts["failed"] += 1
                    failed_for_source += 1
                    _event(logging.ERROR, "invalid_source_url", source_id=source_id_value, error=str(exc))
                    continue
                permitted, reason = self._permitted(source, url)
                if not permitted:
                    skipped_for_source += 1
                    _event(logging.WARNING, "source_url_skipped", source_id=source_id_value, url=url, reason=reason)
                    continue
                prior = new_pages.get(url, {})
                headers = {"Accept": "text/html,application/xhtml+xml;q=0.9"}
                if prior.get("etag"):
                    headers["If-None-Match"] = prior["etag"]
                if prior.get("last_modified"):
                    headers["If-Modified-Since"] = prior["last_modified"]
                try:
                    response = self._request(url, headers)
                    if response.status_code == 304 and prior.get("content_hash"):
                        docs = page_documents[url] if url in page_documents else prior.get("documents", [])
                        candidates = prior.get("candidates", [])
                        page_hash = prior["content_hash"]
                    elif response.status_code == 200:
                        docs, candidates = _extract_page_documents(source, url, response, catalogue, utc_now())
                        validation = validate_documents(docs)
                        if not validation["valid"]:
                            counts["skipped_documents"] += len(docs)
                            raise ValueError(f"extracted documents failed validation: {validation['errors'][:3]}")
                        page_hash = _page_hash(docs)
                    else:
                        raise RuntimeError(f"HTTP {response.status_code}")
                    duplicate_of = seen_page_hashes.get(page_hash)
                    if duplicate_of and duplicate_of != url:
                        counts["duplicates"] += max(1, len(docs))
                        new_pages[url] = {
                            "source_id": source_id_value,
                            "etag": response.headers.get("etag", prior.get("etag")) if response.status_code != 304 else prior.get("etag"),
                            "last_modified": response.headers.get("last-modified", prior.get("last_modified")) if response.status_code != 304 else prior.get("last_modified"),
                            "content_hash": page_hash, "retrieved_at": utc_now(),
                            "document_ids": [], "candidates": [], "duplicate_of": duplicate_of,
                        }
                        page_documents[url] = []
                        successful_for_source += 1
                        _event(logging.INFO, "duplicate_page_skipped", source_id=source_id_value, url=url, duplicate_of=duplicate_of, documents=max(1, len(docs)))
                        continue
                    seen_page_hashes.setdefault(page_hash, url)
                    old_hash = prior.get("content_hash")
                    if response.status_code != 304:
                        counts["new" if not prior else "unchanged" if old_hash == page_hash else "updated"] += len(docs)
                    else:
                        counts["unchanged"] += len(docs)
                    retrieved_at = utc_now()
                    new_pages[url] = {
                        "source_id": source_id_value,
                        "etag": response.headers.get("etag", prior.get("etag")) if response.status_code != 304 else prior.get("etag"),
                        "last_modified": response.headers.get("last-modified", prior.get("last_modified")) if response.status_code != 304 else prior.get("last_modified"),
                        "content_hash": page_hash,
                        "retrieved_at": retrieved_at if response.status_code != 304 else prior.get("retrieved_at"),
                        "document_ids": [document["document_id"] for document in docs],
                        "candidates": candidates,
                    }
                    page_documents[url] = docs
                    successful_for_source += 1
                    _event(logging.INFO, "source_url_collected", source_id=source_id_value, url=url, status_code=response.status_code, documents=len(docs), content_hash=page_hash)
                except Exception as exc:
                    counts["failed"] += 1
                    failed_for_source += 1
                    _event(logging.WARNING, "source_url_failed", source_id=source_id_value, url=url, error_type=type(exc).__name__, message=str(exc))
                    # Retain previous page data when the endpoint is down or changes format.
                    if prior:
                        new_pages[url] = prior
            counts["succeeded"] += successful_for_source
            counts["skipped"] += skipped_for_source
            if successful_for_source:
                source["last_successful_collection"] = utc_now()
            source_results.append({"source_id": source_id_value, "status": "partial_failure" if failed_for_source else "success" if successful_for_source else "unavailable", "succeeded": successful_for_source, "failed": failed_for_source, "skipped": skipped_for_source})

        combined_by_id: dict[str, dict[str, Any]] = {}
        for page_docs in page_documents.values():
            for doc in page_docs:
                if isinstance(doc, dict) and isinstance(doc.get("document_id"), str):
                    combined_by_id[doc["document_id"]] = doc
        collected = sorted(combined_by_id.values(), key=lambda d: d["document_id"])
        candidates_by_id: dict[str, dict[str, Any]] = {}
        for page in new_pages.values():
            for candidate in page.get("candidates", []):
                candidates_by_id[candidate["candidate_id"]] = candidate
        report = {
            "collected_at": utc_now(), "dry_run": dry_run, "counts": counts,
            "source_urls": {key: counts[key] for key in ("attempted", "succeeded", "failed", "skipped")},
            "documents": {key: counts[key] for key in ("new", "updated", "unchanged", "duplicates", "skipped_documents")},
            "sources": source_results, "documents_retained": len(collected),
            "catalogue_candidates_pending_review": len(candidates_by_id),
        }
        if dry_run:
            report["_documents_preview"] = collected
        if not dry_run:
            atomic_write_json(self.collected_path, collected)
            atomic_write_json(self.state_path, {"pages": new_pages, "last_collection": report["collected_at"]})
            atomic_write_json(self.registry_path, registry)
            atomic_write_json(self.catalogue_path.with_name("catalogue_candidates.json"), sorted(candidates_by_id.values(), key=lambda c: c["candidate_id"]))
            self._attach_review_sources(catalogue, collected)
        return report

    def _attach_review_sources(self, catalogue: list[dict[str, Any]], documents: list[dict[str, Any]]) -> None:
        by_id = {item.get("id"): item for item in catalogue if isinstance(item, dict)}
        changed = False
        for doc in documents:
            temple = by_id.get(doc.get("temple_id"))
            if not temple or not doc.get("source_url"):
                continue
            review_sources = temple.setdefault("collected_sources", [])
            if any(source.get("url") == doc["source_url"] for source in review_sources if isinstance(source, dict)):
                continue
            review_sources.append({
                "title": doc.get("source_title", "Collected source"),
                "url": doc["source_url"], "publisher": doc.get("publisher"),
                "verification_status": "needs_review",
            })
            changed = True
        if changed:
            atomic_write_json(self.catalogue_path, catalogue)

