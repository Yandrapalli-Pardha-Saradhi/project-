from __future__ import annotations

import hashlib
import json
import logging
import re
from collections import Counter, defaultdict
from typing import Any, Iterable
from urllib.parse import urlparse

logger = logging.getLogger("temple_heritage.ingestion")
REQUIRED_FIELDS = ("document_id", "source_title", "source_url", "text")


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def merge_documents(*datasets: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge validated records by stable ID; later datasets replace earlier ones."""
    merged: dict[str, dict[str, Any]] = {}
    for dataset in datasets:
        for document in dataset:
            if isinstance(document, dict) and isinstance(document.get("document_id"), str):
                merged[document["document_id"]] = document
    return list(merged.values())


def enrich_catalogue_metadata(documents: list[dict[str, Any]], catalogue: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Copy only already-curated structured fields onto indexed document records."""
    catalogue_by_id = {item.get("id"): item for item in catalogue if isinstance(item, dict)}
    enriched: list[dict[str, Any]] = []
    for source_doc in documents:
        document = dict(source_doc)
        document.setdefault("topic", "general_heritage")
        document.setdefault("language", "und")
        document.setdefault("verification_status", "curated_unverified")
        document.setdefault("source_type", "curated_paraphrase" if document.get("is_paraphrase") else "curated_text")
        if isinstance(document.get("text"), str):
            document.setdefault("content_hash", hashlib.sha256(normalize_whitespace(document["text"]).encode("utf-8")).hexdigest())
        temple = catalogue_by_id.get(document.get("temple_id"))
        if temple:
            names = temple.get("names") or []
            document.setdefault("temple_name", names[0] if names else None)
            for field in ("state", "district"):
                if not document.get(field) and temple.get(field):
                    document[field] = temple[field]
        enriched.append(document)
    return enriched


def validate_documents(documents: list[Any], minimum_text_length: int = 50) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_content: dict[str, str] = {}
    by_temple: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    name_to_ids: dict[str, set[str]] = defaultdict(set)
    missing_fields: Counter[str] = Counter()
    missing_optional_fields: Counter[str] = Counter()

    for index, document in enumerate(documents):
        if not isinstance(document, dict):
            errors.append({"index": index, "message": "document must be a JSON object"})
            continue
        for field in REQUIRED_FIELDS:
            value = document.get(field)
            if not isinstance(value, str) or not value.strip():
                missing_fields[field] += 1
                errors.append({"index": index, "field": field, "message": "required field is missing or empty"})
        for field in ("temple_id", "temple_name", "state", "district", "topic", "language", "publication_date", "retrieval_date", "collection_timestamp", "publisher", "source_type"):
            if document.get(field) in (None, ""):
                missing_optional_fields[field] += 1
        document_id = document.get("document_id")
        if isinstance(document_id, str) and document_id:
            if document_id in seen_ids:
                errors.append({"index": index, "field": "document_id", "message": f"duplicate document id: {document_id}"})
            seen_ids.add(document_id)
        source_url = document.get("source_url")
        if isinstance(source_url, str) and source_url:
            parts = urlparse(source_url)
            if parts.scheme != "https" or not parts.hostname:
                errors.append({"index": index, "field": "source_url", "message": "source URL must be an absolute HTTPS URL"})
        text = document.get("text")
        if isinstance(text, str):
            cleaned = normalize_whitespace(text)
            if len(cleaned) < minimum_text_length:
                errors.append({"index": index, "field": "text", "message": f"document text is suspiciously short ({len(cleaned)} characters)"})
            actual_hash = hashlib.sha256(cleaned.encode("utf-8")).hexdigest()
            provided_hash = document.get("content_hash")
            if provided_hash and provided_hash != actual_hash:
                warnings.append({"index": index, "field": "content_hash", "message": "stored content hash does not match text"})
            if isinstance(source_url, str) and source_url:
                if actual_hash in seen_content and seen_content[actual_hash] != source_url:
                    warnings.append({"index": index, "field": "text", "message": f"duplicate content also appears at {seen_content[actual_hash]}"})
                else:
                    seen_content[actual_hash] = source_url
        temple_id = document.get("temple_id")
        if temple_id is not None and (not isinstance(temple_id, str) or not temple_id.strip()):
            errors.append({"index": index, "field": "temple_id", "message": "temple_id must be null or a non-empty string"})
        if isinstance(temple_id, str) and temple_id:
            for field in ("state", "district"):
                value = document.get(field)
                if isinstance(value, str) and value.strip():
                    by_temple[temple_id][field].add(value.strip().casefold())
            name = document.get("temple_name")
            if isinstance(name, str) and name.strip():
                name_to_ids[re.sub(r"\W+", " ", name.casefold()).strip()].add(temple_id)
        elif isinstance(document.get("temple_name"), str):
            warnings.append({"index": index, "field": "temple_id", "message": "unlinked temple candidate requires review"})
        if document.get("verification_status") not in ("verified", "curated", "curated_unverified", None):
            warnings.append({"index": index, "field": "verification_status", "message": "document is pending human source review"})

    for temple_id, values in by_temple.items():
        for field, observed in values.items():
            if len(observed) > 1:
                warnings.append({"temple_id": temple_id, "field": field, "message": f"conflicting source values: {sorted(observed)}"})
    for name, ids in name_to_ids.items():
        if len(ids) > 1:
            warnings.append({"name": name, "field": "temple_id", "message": f"same normalized name maps to multiple IDs: {sorted(ids)}"})
    return {
        "valid": not errors,
        "documents": len(documents),
        "errors": errors,
        "warnings": warnings,
        "missing_fields": dict(missing_fields),
        "missing_optional_fields": dict(missing_optional_fields),
        "duplicate_content_count": sum("duplicate content" in item["message"] for item in warnings),
    }


def validate_catalogue(catalogue: list[Any]) -> dict[str, Any]:
    """Validate stable IDs and source links without filling unknown facts."""
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, temple in enumerate(catalogue):
        if not isinstance(temple, dict):
            errors.append({"index": index, "message": "temple record must be a JSON object"})
            continue
        temple_id = temple.get("id")
        if not isinstance(temple_id, str) or not temple_id.strip():
            errors.append({"index": index, "field": "id", "message": "stable temple ID is required"})
        elif temple_id in seen_ids:
            errors.append({"index": index, "field": "id", "message": f"duplicate temple ID: {temple_id}"})
        else:
            seen_ids.add(temple_id)
        names = temple.get("names")
        if not isinstance(names, list) or not any(isinstance(name, str) and name.strip() for name in names):
            errors.append({"index": index, "field": "names", "message": "at least one non-empty name is required"})
        sources = list(temple.get("sources") or [])
        location_source = temple.get("location_source")
        if isinstance(location_source, dict):
            sources.append(location_source)
        for source_index, source in enumerate(sources):
            url = source.get("url") if isinstance(source, dict) else None
            parts = urlparse(url) if isinstance(url, str) else None
            if parts is None or parts.scheme != "https" or not parts.hostname:
                errors.append({"index": index, "field": f"sources[{source_index}].url", "message": "source URL must be absolute HTTPS"})
        if not sources:
            warnings.append({"index": index, "field": "sources", "message": "no supporting source links recorded"})
    return {"valid": not errors, "records": len(catalogue), "unique_ids": len(seen_ids), "errors": errors, "warnings": warnings}


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Create sentence-aware chunks with a small overlap for continuity."""
    text = normalize_whitespace(text)
    if not text:
        return []
    if chunk_size <= 0:
        return [text]
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + (1 if current else 0) > chunk_size and current:
            chunks.append(current)
            current = ""
        if len(sentence) > chunk_size:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(sentence[start:start + chunk_size] for start in range(0, len(sentence), chunk_size))
        else:
            current = f"{current} {sentence}".strip()
    if current:
        chunks.append(current)
    if chunk_overlap > 0 and len(chunks) > 1:
        chunks = [chunks[0], *[f"{chunks[i - 1][-chunk_overlap:]} {chunks[i]}" for i in range(1, len(chunks))]]
    return [chunk for chunk in chunks if chunk.strip()]


def build_payload(documents: list[dict[str, Any]], settings: Any) -> tuple[list[str], list[str], list[dict[str, Any]]]:
    ids: list[str] = []
    texts: list[str] = []
    metadatas: list[dict[str, Any]] = []
    for document in documents:
        chunks = chunk_text(document["text"], settings.chunk_size, settings.chunk_overlap)
        normalized_text = normalize_whitespace(document["text"])
        content_hash = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()
        embedding_model = str(getattr(settings, "embedding_model", "unknown"))
        hash_payload = {
            field: document.get(field)
            for field in ("document_id", "source_title", "source_url", "publisher", "temple_id", "temple_name", "state", "district", "topic", "language", "publication_date", "verification_status")
        }
        if document.get("review_status"):
            hash_payload["review_status"] = document["review_status"]
        hash_payload["content_hash"] = content_hash
        document_hash = hashlib.sha256(json.dumps(hash_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
        for index, chunk in enumerate(chunks):
            ids.append(f"{document['document_id']}_chunk_{index}")
            texts.append(chunk)
            metadata: dict[str, Any] = {
                "document_id": document["document_id"],
                "source_title": document["source_title"],
                "source_url": document["source_url"],
                "publisher": str(document.get("publisher") or ""),
                "topic": str(document.get("topic") or "general_heritage"),
                "language": str(document.get("language") or "und"),
                "is_paraphrase": bool(document.get("is_paraphrase", False)),
                "chunk_index": index,
                "document_hash": document_hash,
                "content_hash": content_hash,
                "chunk_hash": hashlib.sha256(f"{embedding_model}\0{chunk}".encode("utf-8")).hexdigest(),
                "embedding_model": embedding_model,
            }
            for field in ("temple_id", "temple_name", "state", "district"):
                value = document.get(field)
                if isinstance(value, (str, int, float, bool)) and str(value).strip():
                    metadata[field] = value
            for field in ("publication_date", "retrieval_date", "collection_timestamp", "verification_status", "review_status", "source_type", "taluk"):
                value = document.get(field)
                if isinstance(value, (str, int, float, bool)) and str(value).strip():
                    metadata[field] = value
            metadatas.append(metadata)
    return ids, texts, metadatas


def index_documents(
    documents: list[dict[str, Any]], collection: Any, embedding_service: Any,
    settings: Any, dry_run: bool = False,
) -> dict[str, Any]:
    validation = validate_documents(documents)
    if not validation["valid"]:
        raise ValueError(f"refusing to index invalid data: {validation['errors'][:5]}")
    ids, texts, metadatas = build_payload(documents, settings)
    if not ids:
        raise ValueError("refusing to index an empty chunk set")
    before_count = collection.count() if collection is not None else 0
    existing = collection.get(include=["metadatas", "documents"]) if collection is not None else {"ids": [], "metadatas": [], "documents": []}
    existing_metadata = dict(zip(existing.get("ids", []), existing.get("metadatas", [])))
    existing_documents = dict(zip(existing.get("ids", []), existing.get("documents", [])))
    pending_indices: list[int] = []
    metadata_indices: list[int] = []
    for index, (chunk_id, metadata, text) in enumerate(zip(ids, metadatas, texts)):
        old_metadata = existing_metadata.get(chunk_id)
        if not isinstance(old_metadata, dict) or existing_documents.get(chunk_id) != text:
            pending_indices.append(index)
            continue
        # Legacy chunks have no hashes. Their stored text is the authoritative
        # embedding input, so backfill hashes/provenance without re-embedding.
        if old_metadata.get("chunk_hash") is not None and old_metadata["chunk_hash"] != metadata["chunk_hash"]:
            pending_indices.append(index)
            continue
        if any(old_metadata.get(key) != value for key, value in metadata.items()):
            metadata_indices.append(index)
    current_ids = set(ids)
    active_document_ids = {document["document_id"] for document in documents}
    stale_ids = [
        chunk_id for chunk_id, metadata in zip(existing.get("ids", []), existing.get("metadatas", []))
        if isinstance(metadata, dict) and metadata.get("document_id") and metadata.get("source_url")
        and (metadata["document_id"] not in active_document_ids or chunk_id not in current_ids)
    ]
    old_document_ids = {
        metadata["document_id"] for metadata in existing_metadata.values()
        if isinstance(metadata, dict) and metadata.get("document_id") and metadata.get("source_url")
    }
    pending_id_set = {ids[index] for index in pending_indices}
    metadata_id_set = {ids[index] for index in metadata_indices}
    document_chunks: dict[str, list[str]] = defaultdict(list)
    for chunk_id, metadata in zip(ids, metadatas):
        document_chunks[str(metadata["document_id"])].append(chunk_id)
    documents_added = sum(not any(chunk_id in existing_metadata for chunk_id in chunk_ids) for chunk_ids in document_chunks.values())
    documents_updated = sum(
        any(chunk_id in existing_metadata for chunk_id in chunk_ids)
        and any(chunk_id in pending_id_set or chunk_id in metadata_id_set for chunk_id in chunk_ids)
        for chunk_ids in document_chunks.values()
    )
    documents_unchanged = len(document_chunks) - documents_added - documents_updated
    removed_document_ids = old_document_ids - active_document_ids
    report = {
        "documents": len(documents), "chunks_total": len(ids),
        "documents_added": documents_added, "documents_updated": documents_updated,
        "documents_unchanged": documents_unchanged, "documents_removed": len(removed_document_ids),
        "documents_failed": 0,
        "chunks_to_upsert": len(pending_indices), "chunks_added": sum(ids[index] not in existing_metadata for index in pending_indices),
        "chunks_updated": sum(ids[index] in existing_metadata for index in pending_indices),
        "chunks_metadata_update": len(metadata_indices),
        "chunks_unchanged": len(ids) - len(pending_indices) - len(metadata_indices),
        "chunks_before": before_count, "dry_run": dry_run,
        "stale_chunks_to_delete": len(stale_ids), "stale_chunks_deleted": 0,
        "chunks_removed": len(stale_ids), "chunks_failed": 0,
        "duplicate_documents": validation["duplicate_content_count"],
    }
    if dry_run:
        return report
    embeddings = embedding_service.embed_texts([texts[index] for index in pending_indices]) if pending_indices else []
    # Upsert before any deletion: failed embedding/upsert leaves the old index intact.
    if pending_indices:
        collection.upsert(
            ids=[ids[index] for index in pending_indices],
            documents=[texts[index] for index in pending_indices],
            metadatas=[metadatas[index] for index in pending_indices],
            embeddings=embeddings,
        )
    if metadata_indices:
        collection.update(
            ids=[ids[index] for index in metadata_indices],
            metadatas=[metadatas[index] for index in metadata_indices],
        )
    if stale_ids:
        collection.delete(ids=stale_ids)
    report["stale_chunks_deleted"] = len(stale_ids)
    report["chunks_after"] = collection.count()
    return report


def summarize_report(catalogue: list[dict[str, Any]], documents: list[dict[str, Any]], indexed_chunks: int, sources: list[dict[str, Any]]) -> dict[str, Any]:
    states: Counter[str] = Counter()
    districts: Counter[str] = Counter()
    missing: Counter[str] = Counter()
    for temple in catalogue:
        for field in ("canonical_name", "alternate_names", "state", "district", "area", "coordinates", "deities", "architectural_style", "historical_period", "important_festivals", "official_website_url", "description", "sources", "last_verified"):
            if not temple.get(field):
                missing[field] += 1
        if temple.get("state"):
            states[str(temple["state"])] += 1
        if temple.get("district"):
            districts[str(temple["district"])] += 1
    return {
        "catalogue_records_total": len(catalogue),
        "catalogue_unique_temple_ids": len({item.get("id") for item in catalogue if isinstance(item.get("id"), str) and item.get("id")}),
        "catalogue_records_explicitly_verified": sum(item.get("verification_status") == "verified" for item in catalogue),
        "catalogue_records_unverified": sum(item.get("verification_status") != "verified" for item in catalogue),
        "catalogue_records_curated_without_explicit_verification_flag": sum(not item.get("verification_status") for item in catalogue),
        "knowledge_documents_total": len(documents),
        "knowledge_documents_linked_to_catalogue_temple_ids": len({item.get("temple_id") for item in documents if item.get("temple_id") in {entry.get("id") for entry in catalogue if isinstance(entry, dict)}}),
        "knowledge_documents_explicitly_verified": sum(item.get("verification_status") == "verified" for item in documents),
        "indexed_chunks": indexed_chunks,
        "records_by_state": dict(sorted(states.items())),
        "records_by_district": dict(sorted(districts.items())),
        "missing_catalogue_fields": dict(missing),
        "sources": sources,
        "validation": validate_documents(documents),
    }

