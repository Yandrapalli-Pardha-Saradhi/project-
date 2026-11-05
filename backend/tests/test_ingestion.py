from __future__ import annotations

import json
from types import SimpleNamespace

import httpx
import pytest
import chromadb

from app.services.collection_service import CollectionEngine, _extract_page_documents, stable_id
from app.services.ingestion_service import build_payload, enrich_catalogue_metadata, index_documents, validate_catalogue, validate_documents


GOOD_HTML = """<!doctype html><html lang="en"><head><title>Temple history</title>
<link rel="canonical" href="https://heritage.example/temple" /></head>
<body><nav>Home Search Menu</nav><script>ignore this</script><main><h1>Temple history</h1>
<p>This is a sufficiently detailed historical page about the temple architecture, inscriptions and cultural heritage.</p>
<p>The page retains its source attribution for later review and RAG citations.</p></main><footer>Cookie settings</footer></body></html>"""


def _source(**overrides):
    source = {
        "id": "fixture", "name": "Fixture Heritage Office", "category": "test",
        "enabled": True, "terms_review_status": "approved",
        "permitted_collection_method": "explicit_public_html_robots_checked",
        "allowed_hosts": ["heritage.example"],
        "start_urls": ["https://heritage.example/temple"], "parser": "generic_html",
    }
    source.update(overrides)
    return source


def _document(document_id="doc-a", text=None):
    return {
        "document_id": document_id,
        "temple_id": "temple-a",
        "temple_name": "Temple A",
        "state": "Tamil Nadu",
        "district": "District A",
        "topic": "history",
        "source_title": "Temple A history",
        "source_url": "https://heritage.example/temple",
        "publisher": "Fixture source",
        "language": "en",
        "text": text or "A sufficiently detailed source passage about the temple and its documented history.",
    }


def test_html_extraction_cleans_boilerplate_and_keeps_metadata():
    source = _source()
    response = httpx.Response(200, headers={"content-type": "text/html"}, text=GOOD_HTML, request=httpx.Request("GET", source["start_urls"][0]))
    docs, candidates = _extract_page_documents(source, source["start_urls"][0], response, [], "2026-11-04T00:00:00+00:00")
    assert not candidates
    assert len(docs) == 1
    doc = docs[0]
    assert doc["source_title"] == "Temple history"
    assert doc["source_url"] == "https://heritage.example/temple"
    assert doc["language"] == "en"
    assert "ignore this" not in doc["text"]
    assert "Cookie settings" not in doc["text"]
    assert "Home Search Menu" not in doc["text"]
    assert doc["verification_status"] == "source_attributed_needs_review"


def test_tamil_archaeology_table_produces_review_candidates_and_stable_ids():
    source = _source(parser="tn_arch_temple_table", state_context="Tamil Nadu")
    html = """<html lang="en"><head><title>Temple listing</title></head><body><table>
    <tr><th>S.No</th><th>Name of the Temples</th><th>Taluk</th><th>District</th></tr>
    <tr><td>1</td><td>Example Temple</td><td>Example Taluk</td><td>Example District</td></tr>
    </table></body></html>"""
    request = httpx.Request("GET", source["start_urls"][0])
    response = httpx.Response(200, headers={"content-type": "text/html"}, text=html, request=request)
    docs, candidates = _extract_page_documents(source, source["start_urls"][0], response, [], "2026-11-04T00:00:00+00:00")
    assert docs[0]["temple_id"] is None
    assert docs[0]["state"] == "Tamil Nadu"
    assert docs[0]["taluk"] == "Example Taluk"
    assert docs[0]["district"] == "Example District"
    assert "Example Temple" in docs[0]["text"]
    assert candidates[0]["verification_status"] == "needs_review"
    assert docs[0]["document_id"] == stable_id("https://heritage.example/temple|example temple")


def test_validation_rejects_missing_or_invalid_source_urls():
    missing = _document()
    missing["source_url"] = ""
    invalid = _document("doc-b")
    invalid["source_url"] = "file:///private/page.html"
    report = validate_documents([missing, invalid])
    assert report["valid"] is False
    assert any(error.get("field") == "source_url" for error in report["errors"])


def test_catalogue_validation_rejects_duplicate_ids_and_bad_sources():
    catalogue = [
        {"id": "temple-a", "names": ["Temple A"], "sources": [{"url": "https://example.org/source"}]},
        {"id": "temple-a", "names": ["Temple A alias"], "sources": [{"url": "javascript:alert(1)"}]},
    ]
    report = validate_catalogue(catalogue)
    assert report["valid"] is False
    assert any("duplicate temple ID" in item["message"] for item in report["errors"])
    assert any("absolute HTTPS" in item["message"] for item in report["errors"])


def test_document_validation_rejects_duplicate_ids():
    report = validate_documents([_document("same-id"), _document("same-id")])
    assert report["valid"] is False
    assert any("duplicate document id" in item["message"] for item in report["errors"])


def test_collection_incremental_etag_and_duplicate_free_output(tmp_path):
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, headers={"content-type": "text/plain"}, text="User-agent: *\nAllow: /", request=request)
        if request.headers.get("if-none-match") == '"fixture-v1"':
            return httpx.Response(304, request=request)
        return httpx.Response(200, headers={"content-type": "text/html", "etag": '"fixture-v1"'}, text=GOOD_HTML, request=request)

    registry_path = tmp_path / "source_registry.json"
    collected_path = tmp_path / "collected.json"
    state_path = tmp_path / "state.json"
    catalogue_path = tmp_path / "catalogue.json"
    registry_path.write_text(json.dumps({"sources": [_source()]}), encoding="utf-8")
    catalogue_path.write_text("[]", encoding="utf-8")
    transport = httpx.MockTransport(handler)
    first_client = httpx.Client(transport=transport)
    first_engine = CollectionEngine(registry_path, collected_path, state_path, catalogue_path, client=first_client, min_domain_interval=0)
    first = first_engine.collect()
    first_engine.close()
    first_docs = json.loads(collected_path.read_text(encoding="utf-8"))
    saved_registry = json.loads(registry_path.read_text(encoding="utf-8"))
    second_client = httpx.Client(transport=transport)
    second_engine = CollectionEngine(registry_path, collected_path, state_path, catalogue_path, client=second_client, min_domain_interval=0)
    second = second_engine.collect()
    second_engine.close()
    second_docs = json.loads(collected_path.read_text(encoding="utf-8"))
    assert first["counts"]["new"] == 1
    assert second["counts"]["unchanged"] == 1
    assert len(first_docs) == len(second_docs) == 1
    assert any(call.headers.get("if-none-match") == '"fixture-v1"' for call in calls)
    assert saved_registry["sources"][0]["last_successful_collection"]


def test_incremental_content_change_keeps_document_id_and_updates_hash(tmp_path):
    call_count = 0
    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        if request.url.path == "/robots.txt":
            return httpx.Response(200, headers={"content-type": "text/plain"}, text="User-agent: *\nAllow: /", request=request)
        call_count += 1
        body = GOOD_HTML if call_count == 1 else GOOD_HTML.replace("cultural heritage", "regional cultural preservation")
        etag = '"version-1"' if call_count == 1 else '"version-2"'
        return httpx.Response(200, headers={"content-type": "text/html", "etag": etag}, text=body, request=request)
    registry_path = tmp_path / "registry.json"
    collected_path = tmp_path / "collected.json"
    state_path = tmp_path / "state.json"
    catalogue_path = tmp_path / "catalogue.json"
    registry_path.write_text(json.dumps({"sources": [_source()]}), encoding="utf-8")
    catalogue_path.write_text("[]", encoding="utf-8")
    for _ in range(2):
        engine = CollectionEngine(registry_path, collected_path, state_path, catalogue_path, client=httpx.Client(transport=httpx.MockTransport(handler)), min_domain_interval=0)
        report = engine.collect()
        engine.close()
    docs = json.loads(collected_path.read_text(encoding="utf-8"))
    assert report["counts"]["updated"] == 1
    assert docs[0]["document_id"] == stable_id("https://heritage.example/temple")
    assert "regional cultural preservation" in docs[0]["text"]


def test_identical_pages_at_different_urls_are_deduplicated(tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(200, headers={"content-type": "text/plain"}, text="User-agent: *\nAllow: /", request=request)
        return httpx.Response(200, headers={"content-type": "text/html"}, text=GOOD_HTML, request=request)
    registry_path = tmp_path / "registry.json"
    collected_path = tmp_path / "collected.json"
    state_path = tmp_path / "state.json"
    catalogue_path = tmp_path / "catalogue.json"
    source = _source(start_urls=["https://heritage.example/temple", "https://heritage.example/copy"])
    registry_path.write_text(json.dumps({"sources": [source]}), encoding="utf-8")
    catalogue_path.write_text("[]", encoding="utf-8")
    engine = CollectionEngine(registry_path, collected_path, state_path, catalogue_path, client=httpx.Client(transport=httpx.MockTransport(handler)), min_domain_interval=0)
    report = engine.collect()
    engine.close()
    assert report["counts"]["duplicates"] == 1
    assert report["documents_retained"] == 1


def test_partial_source_failure_keeps_successful_and_prior_documents(tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(200, headers={"content-type": "text/plain"}, text="User-agent: *\nAllow: /", request=request)
        if request.url.path == "/bad":
            return httpx.Response(503, request=request)
        return httpx.Response(200, headers={"content-type": "text/html"}, text=GOOD_HTML, request=request)

    registry_path = tmp_path / "registry.json"
    collected_path = tmp_path / "collected.json"
    state_path = tmp_path / "state.json"
    catalogue_path = tmp_path / "catalogue.json"
    registry_path.write_text(json.dumps({"sources": [_source(start_urls=["https://heritage.example/ok", "https://heritage.example/bad"])]}), encoding="utf-8")
    catalogue_path.write_text("[]", encoding="utf-8")
    engine = CollectionEngine(registry_path, collected_path, state_path, catalogue_path, client=httpx.Client(transport=httpx.MockTransport(handler)), retries=0, min_domain_interval=0)
    report = engine.collect()
    engine.close()
    assert report["counts"]["succeeded"] == 1
    assert report["counts"]["failed"] == 1
    assert len(json.loads(collected_path.read_text(encoding="utf-8"))) == 1


def test_failed_refresh_preserves_previous_page_document(tmp_path):
    def make_handler(fail: bool):
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/robots.txt":
                return httpx.Response(200, headers={"content-type": "text/plain"}, text="User-agent: *\nAllow: /", request=request)
            if fail:
                return httpx.Response(503, request=request)
            return httpx.Response(200, headers={"content-type": "text/html"}, text=GOOD_HTML, request=request)
        return handler
    registry_path = tmp_path / "registry.json"
    collected_path = tmp_path / "collected.json"
    state_path = tmp_path / "state.json"
    catalogue_path = tmp_path / "catalogue.json"
    registry_path.write_text(json.dumps({"sources": [_source()]}), encoding="utf-8")
    catalogue_path.write_text("[]", encoding="utf-8")
    for fail in (False, True):
        engine = CollectionEngine(registry_path, collected_path, state_path, catalogue_path, client=httpx.Client(transport=httpx.MockTransport(make_handler(fail))), retries=0, min_domain_interval=0)
        report = engine.collect()
        engine.close()
    docs = json.loads(collected_path.read_text(encoding="utf-8"))
    assert report["counts"]["failed"] == 1
    assert len(docs) == 1 and docs[0]["source_title"] == "Temple history"


def test_dry_run_does_not_write_collection_artifacts(tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(200, headers={"content-type": "text/plain"}, text="User-agent: *\nAllow: /", request=request)
        return httpx.Response(200, headers={"content-type": "text/html"}, text=GOOD_HTML, request=request)

    registry_path = tmp_path / "registry.json"
    collected_path = tmp_path / "collected.json"
    state_path = tmp_path / "state.json"
    catalogue_path = tmp_path / "catalogue.json"
    registry_path.write_text(json.dumps({"sources": [_source()]}), encoding="utf-8")
    catalogue_path.write_text("[]", encoding="utf-8")
    engine = CollectionEngine(registry_path, collected_path, state_path, catalogue_path, client=httpx.Client(transport=httpx.MockTransport(handler)), min_domain_interval=0)
    report = engine.collect(dry_run=True)
    engine.close()
    assert report["dry_run"] is True
    assert len(report["_documents_preview"]) == 1
    assert not collected_path.exists()
    assert not state_path.exists()


def test_collection_gate_requires_terms_approval(tmp_path):
    requests = []
    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, headers={"content-type": "text/html"}, text=GOOD_HTML, request=request)
    registry_path = tmp_path / "registry.json"
    collected_path = tmp_path / "collected.json"
    state_path = tmp_path / "state.json"
    catalogue_path = tmp_path / "catalogue.json"
    source = _source(terms_review_status="operator_must_confirm_before_scheduled_runs")
    registry_path.write_text(json.dumps({"sources": [source]}), encoding="utf-8")
    catalogue_path.write_text("[]", encoding="utf-8")
    engine = CollectionEngine(registry_path, collected_path, state_path, catalogue_path, client=httpx.Client(transport=httpx.MockTransport(handler)), min_domain_interval=0)
    report = engine.collect()
    engine.close()
    assert requests == []
    assert report["sources"][0]["status"] == "terms_review_required"
    assert report["source_urls"]["skipped"] == 1


def test_explicit_sitemap_only_adds_allowlisted_paths(tmp_path):
    requested = []
    def handler(request: httpx.Request) -> httpx.Response:
        requested.append(str(request.url))
        if request.url.path == "/robots.txt":
            return httpx.Response(200, headers={"content-type": "text/plain"}, text="User-agent: *\nAllow: /", request=request)
        if request.url.path == "/sitemap.xml":
            body = """<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://heritage.example/temples/one</loc></url>
            <url><loc>https://heritage.example/news/latest</loc></url>
            <url><loc>https://outside.example/temples/two</loc></url></urlset>"""
            return httpx.Response(200, headers={"content-type": "application/xml"}, text=body, request=request)
        return httpx.Response(200, headers={"content-type": "text/html"}, text=GOOD_HTML, request=request)
    registry_path = tmp_path / "registry.json"
    collected_path = tmp_path / "collected.json"
    state_path = tmp_path / "state.json"
    catalogue_path = tmp_path / "catalogue.json"
    source = _source(start_urls=[], sitemap_urls=["https://heritage.example/sitemap.xml"], sitemap_path_prefixes=["/temples/"])
    registry_path.write_text(json.dumps({"sources": [source]}), encoding="utf-8")
    catalogue_path.write_text("[]", encoding="utf-8")
    engine = CollectionEngine(registry_path, collected_path, state_path, catalogue_path, client=httpx.Client(transport=httpx.MockTransport(handler)), min_domain_interval=0)
    report = engine.collect()
    engine.close()
    assert report["source_urls"]["attempted"] == 1
    assert "https://heritage.example/temples/one" in requested
    assert "https://heritage.example/news/latest" not in requested
    assert not any("outside.example" in url for url in requested)


def test_robots_disallow_prevents_page_request(tmp_path):
    requested = []
    def handler(request: httpx.Request) -> httpx.Response:
        requested.append(request.url.path)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, headers={"content-type": "text/plain"}, text="User-agent: *\nDisallow: /temple", request=request)
        return httpx.Response(200, headers={"content-type": "application/pdf"}, content=b"not html", request=request)
    registry_path = tmp_path / "registry.json"
    collected_path = tmp_path / "collected.json"
    state_path = tmp_path / "state.json"
    catalogue_path = tmp_path / "catalogue.json"
    registry_path.write_text(json.dumps({"sources": [_source()]}), encoding="utf-8")
    catalogue_path.write_text("[]", encoding="utf-8")
    engine = CollectionEngine(registry_path, collected_path, state_path, catalogue_path, client=httpx.Client(transport=httpx.MockTransport(handler)), retries=0, min_domain_interval=0)
    report = engine.collect()
    engine.close()
    assert report["counts"]["skipped"] == 1
    assert report["counts"]["succeeded"] == 0
    assert requested == ["/robots.txt"]


def test_unsupported_content_type_is_reported_without_import(tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(200, headers={"content-type": "text/plain"}, text="User-agent: *\nAllow: /", request=request)
        return httpx.Response(200, headers={"content-type": "application/pdf"}, content=b"not html", request=request)
    registry_path = tmp_path / "registry.json"
    collected_path = tmp_path / "collected.json"
    state_path = tmp_path / "state.json"
    catalogue_path = tmp_path / "catalogue.json"
    registry_path.write_text(json.dumps({"sources": [_source()]}), encoding="utf-8")
    catalogue_path.write_text("[]", encoding="utf-8")
    engine = CollectionEngine(registry_path, collected_path, state_path, catalogue_path, client=httpx.Client(transport=httpx.MockTransport(handler)), retries=0, min_domain_interval=0)
    report = engine.collect()
    engine.close()
    assert report["counts"]["failed"] == 1
    assert report["documents_retained"] == 0


def test_catalogue_links_collected_sources_as_needs_review(tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(200, headers={"content-type": "text/plain"}, text="User-agent: *\nAllow: /", request=request)
        return httpx.Response(200, headers={"content-type": "text/html"}, text=GOOD_HTML, request=request)
    registry_path = tmp_path / "registry.json"
    collected_path = tmp_path / "collected.json"
    state_path = tmp_path / "state.json"
    catalogue_path = tmp_path / "catalogue.json"
    catalogue = [{"id": "temple-a", "names": ["Temple history"], "sources": [{"title": "Curated", "url": "https://curated.example/source"}]}]
    registry_path.write_text(json.dumps({"sources": [_source()]}), encoding="utf-8")
    catalogue_path.write_text(json.dumps(catalogue), encoding="utf-8")
    engine = CollectionEngine(registry_path, collected_path, state_path, catalogue_path, client=httpx.Client(transport=httpx.MockTransport(handler)), min_domain_interval=0)
    engine.collect()
    engine.close()
    updated = json.loads(catalogue_path.read_text(encoding="utf-8"))[0]
    assert updated["sources"] == catalogue[0]["sources"]
    assert updated["collected_sources"][0]["verification_status"] == "needs_review"


class FakeCollection:
    def __init__(self):
        self.rows = {}
        self.fail_upsert = False

    def count(self):
        return len(self.rows)

    def upsert(self, ids, documents, metadatas, embeddings):
        if self.fail_upsert:
            raise RuntimeError("simulated Chroma failure")
        for chunk_id, text, metadata in zip(ids, documents, metadatas):
            self.rows[chunk_id] = {"document": text, "metadata": metadata}

    def get(self, include):
        return {
            "ids": list(self.rows),
            "metadatas": [row["metadata"] for row in self.rows.values()],
            "documents": [row["document"] for row in self.rows.values()],
        }

    def update(self, ids, metadatas):
        for chunk_id, metadata in zip(ids, metadatas):
            self.rows[chunk_id]["metadata"] = metadata

    def delete(self, ids):
        for chunk_id in ids:
            self.rows.pop(chunk_id, None)


class FakeEmbeddings:
    def __init__(self):
        self.calls = 0

    def embed_texts(self, texts):
        self.calls += len(texts)
        return [[1.0, 0.0] for _ in texts]


def test_payload_preserves_citation_and_filter_metadata():
    settings = SimpleNamespace(chunk_size=1000, chunk_overlap=0)
    document = _document()
    document["review_status"] = "pending_human_review"
    enriched = enrich_catalogue_metadata([document], [{"id": "temple-a", "names": ["Temple A"], "state": "Tamil Nadu", "district": "District A"}])
    ids, _texts, metadatas = build_payload(enriched, settings)
    assert ids == ["doc-a_chunk_0"]
    assert metadatas[0]["source_url"] == "https://heritage.example/temple"
    assert metadatas[0]["temple_id"] == "temple-a"
    assert metadatas[0]["state"] == "Tamil Nadu"
    assert metadatas[0]["district"] == "District A"
    assert metadatas[0]["topic"] == "history"
    assert metadatas[0]["language"] == "en"
    assert metadatas[0]["verification_status"] == "curated_unverified"
    assert metadatas[0]["review_status"] == "pending_human_review"
    assert metadatas[0]["content_hash"]
    assert metadatas[0]["embedding_model"] == "unknown"


def test_chunk_ids_and_hashes_are_deterministic_and_model_aware():
    document = _document()
    settings = SimpleNamespace(chunk_size=1000, chunk_overlap=0, embedding_model="model-a")
    first = build_payload([document], settings)
    second = build_payload([document], settings)
    other_model = build_payload([document], SimpleNamespace(chunk_size=1000, chunk_overlap=0, embedding_model="model-b"))
    assert first == second
    assert first[0] == other_model[0]
    assert first[2][0]["chunk_hash"] != other_model[2][0]["chunk_hash"]


def test_index_upserts_and_removes_stale_chunks_only_after_success():
    settings = SimpleNamespace(chunk_size=80, chunk_overlap=0)
    collection = FakeCollection()
    long_text = "First sentence. " * 10 + "Final sentence."
    first = _document("doc-a", long_text)
    report = index_documents([first, _document("doc-b")], collection, FakeEmbeddings(), settings)
    initial_chunk_count = report["chunks_after"]
    assert initial_chunk_count > 2
    assert "doc-a_chunk_1" in collection.rows
    shorter = _document("doc-a", "This source describes its temple history, art, worship, and heritage.")
    report = index_documents([shorter], collection, FakeEmbeddings(), settings)
    assert report["stale_chunks_deleted"] == initial_chunk_count - 1
    assert set(collection.rows) == {"doc-a_chunk_0"}


def test_dry_run_and_upsert_failure_preserve_existing_index():
    settings = SimpleNamespace(chunk_size=1000, chunk_overlap=0)
    collection = FakeCollection()
    index_documents([_document()], collection, FakeEmbeddings(), settings)
    before = dict(collection.rows)
    dry_report = index_documents([_document("doc-b")], collection, None, settings, dry_run=True)
    assert dry_report["dry_run"] is True
    assert dry_report["stale_chunks_to_delete"] == 1
    assert collection.rows == before
    collection.fail_upsert = True
    with pytest.raises(RuntimeError, match="simulated Chroma failure"):
        index_documents([_document("doc-b")], collection, FakeEmbeddings(), settings)
    assert collection.rows == before


def test_reindexing_unchanged_documents_skips_embedding_and_upsert():
    settings = SimpleNamespace(chunk_size=1000, chunk_overlap=0)
    collection = FakeCollection()
    embeddings = FakeEmbeddings()
    first = index_documents([_document()], collection, embeddings, settings)
    second = index_documents([_document()], collection, embeddings, settings)
    assert first["chunks_to_upsert"] == 1
    assert second["chunks_to_upsert"] == 0
    assert second["chunks_unchanged"] == 1
    assert embeddings.calls == 1


def test_legacy_chunks_are_metadata_migrated_without_reembedding():
    settings = SimpleNamespace(chunk_size=1000, chunk_overlap=0)
    collection = FakeCollection()
    document = _document()
    ids, texts, metadata = build_payload([document], settings)
    legacy_metadata = {key: value for key, value in metadata[0].items() if key not in {"chunk_hash", "content_hash", "document_hash"}}
    collection.upsert(ids=ids, documents=texts, metadatas=[legacy_metadata], embeddings=[[1.0, 0.0]])
    embeddings = FakeEmbeddings()

    first = index_documents([document], collection, embeddings, settings, dry_run=True)
    second = index_documents([document], collection, embeddings, settings, dry_run=True)
    assert first["chunks_to_upsert"] == 0
    assert first["chunks_metadata_update"] == 1
    assert second == first
    assert "chunk_hash" not in collection.rows[ids[0]]["metadata"]
    actual = index_documents([document], collection, embeddings, settings)
    assert actual["chunks_to_upsert"] == 0
    assert actual["chunks_metadata_update"] == 1
    assert collection.rows[ids[0]]["metadata"]["chunk_hash"] == metadata[0]["chunk_hash"]
    next_dry_run = index_documents([document], collection, None, settings, dry_run=True)
    assert next_dry_run["chunks_metadata_update"] == 0
    assert next_dry_run["chunks_unchanged"] == 1
    assert embeddings.calls == 0


def test_provenance_change_updates_metadata_without_reembedding():
    settings = SimpleNamespace(chunk_size=1000, chunk_overlap=0)
    collection = FakeCollection()
    embeddings = FakeEmbeddings()
    original = _document()
    index_documents([original], collection, embeddings, settings)
    changed_source = {**original, "source_title": "Updated source title"}
    report = index_documents([changed_source], collection, embeddings, settings)
    assert report["chunks_to_upsert"] == 0
    assert report["chunks_metadata_update"] == 1
    assert collection.rows["doc-a_chunk_0"]["metadata"]["source_title"] == "Updated source title"
    assert embeddings.calls == 1


def test_chroma_persistence_and_metadata_filter_after_reopen(tmp_path):
    path = str(tmp_path / "persistent-chroma")
    settings = SimpleNamespace(chunk_size=1000, chunk_overlap=0, embedding_model="fixture-model")
    client = chromadb.PersistentClient(path=path, settings=chromadb.Settings(anonymized_telemetry=False))
    collection = client.get_or_create_collection("heritage_test", metadata={"hnsw:space": "cosine"})
    index_documents([_document()], collection, FakeEmbeddings(), settings)
    client = None

    reopened = chromadb.PersistentClient(path=path, settings=chromadb.Settings(anonymized_telemetry=False))
    persisted = reopened.get_collection("heritage_test")
    assert persisted.count() == 1
    filtered = persisted.get(where={"district": "District A"}, include=["metadatas"])
    assert filtered["ids"] == ["doc-a_chunk_0"]
    assert filtered["metadatas"][0]["source_url"] == "https://heritage.example/temple"
