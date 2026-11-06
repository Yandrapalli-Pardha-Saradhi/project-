from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

from app.config import DATA_DIR, RAW_DATA_PATH, Settings
from app.services.collection_service import CollectionEngine, _read_json, atomic_write_json
from app.services.embedding_service import EmbeddingService
from app.services.ingestion_service import enrich_catalogue_metadata, index_documents, merge_documents, summarize_report, validate_catalogue, validate_documents
from app.services.retrieval_service import RetrievalService

COLLECTED_DIR = DATA_DIR / "collected"
COLLECTED_PATH = COLLECTED_DIR / "temple_sources.json"
STATE_PATH = COLLECTED_DIR / "collection_state.json"
REGISTRY_PATH = DATA_DIR / "source_registry.json"
CATALOGUE_PATH = DATA_DIR / "catalogue.json"
REPORT_PATH = DATA_DIR / "ingestion_report.json"
COLLECTION_REPORT_PATH = DATA_DIR / "collection_report.json"
INDEX_REPORT_PATH = DATA_DIR / "index_report.json"
VALIDATION_REPORT_PATH = DATA_DIR / "validation_report.json"


def load_datasets() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    raw = _read_json(RAW_DATA_PATH, [])
    collected = _read_json(COLLECTED_PATH, [])
    catalogue = _read_json(CATALOGUE_PATH, [])
    if not isinstance(raw, list) or not isinstance(collected, list) or not isinstance(catalogue, list):
        raise ValueError("raw documents, collected documents, and catalogue must be JSON arrays")
    return enrich_catalogue_metadata(raw, catalogue), enrich_catalogue_metadata(collected, catalogue), catalogue


def _persist_report(path: Path, report: dict[str, Any]) -> None:
    atomic_write_json(path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


def command_collect(args: argparse.Namespace, include_preview: bool = False) -> dict[str, Any]:
    settings = Settings()
    engine = CollectionEngine(
        REGISTRY_PATH, COLLECTED_PATH, STATE_PATH, CATALOGUE_PATH,
        timeout=settings.collector_timeout_seconds,
        retries=settings.collector_retries,
        backoff_seconds=settings.collector_backoff_seconds,
        min_domain_interval=settings.collector_min_domain_interval,
    )
    try:
        result = engine.collect(source_id=args.source, dry_run=args.dry_run)
    finally:
        engine.close()
    preview_documents = result.pop("_documents_preview", [])
    if include_preview and args.dry_run:
        result["_documents_preview"] = preview_documents
    printable = {key: value for key, value in result.items() if not key.startswith("_")}
    if not args.dry_run:
        _persist_report(COLLECTION_REPORT_PATH, printable)
    else:
        print(json.dumps(printable, ensure_ascii=False, indent=2))
    return result


def command_validate(args: argparse.Namespace) -> dict[str, Any]:
    raw, collected, catalogue = load_datasets()
    documents = merge_documents(raw, collected)
    report = validate_documents(documents)
    report["catalogue"] = validate_catalogue(catalogue)
    report["curated_documents"] = len(raw)
    report["collected_documents"] = len(collected)
    if not args.dry_run:
        atomic_write_json(VALIDATION_REPORT_PATH, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["valid"] or not report["catalogue"]["valid"]:
        raise SystemExit(1)
    return report


def _open_index(settings: Settings) -> tuple[EmbeddingService, RetrievalService]:
    embedding_service = EmbeddingService.from_settings(settings)
    retrieval_service = RetrievalService(embedding_service, settings.chroma_persist_dir, settings.collection_name)
    return embedding_service, retrieval_service


def command_index(args: argparse.Namespace, documents_override: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    raw, collected, catalogue = load_datasets()
    documents = documents_override if documents_override is not None else merge_documents(raw, collected)
    settings = Settings()
    if args.dry_run:
        from app.sqlite_compat import ensure_supported_sqlite
        ensure_supported_sqlite()
        import chromadb
        client = chromadb.PersistentClient(path=settings.chroma_persist_dir, settings=chromadb.Settings(anonymized_telemetry=False))
        try:
            collection = client.get_collection(name=settings.collection_name)
        except Exception:
            collection = None
        embedding_service = None
    else:
        embedding_service, retrieval_service = _open_index(settings)
        collection = retrieval_service.collection
    report = index_documents(
        documents, collection, embedding_service, settings,
        dry_run=args.dry_run,
    )
    report.update({
        "collection": settings.collection_name,
        "persist_directory": settings.chroma_persist_dir,
        "curated_documents": len(raw),
        "collected_documents": len(collected),
    })
    if not args.dry_run:
        _persist_report(INDEX_REPORT_PATH, report)
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def command_run(args: argparse.Namespace) -> dict[str, Any]:
    collection_args = argparse.Namespace(source=None, dry_run=args.dry_run)
    collection_report = command_collect(collection_args, include_preview=args.dry_run)
    raw, collected, _catalogue = load_datasets()
    collected = collection_report.pop("_documents_preview", collected) if args.dry_run else collected
    prospective_documents = merge_documents(raw, collected)
    validation = validate_documents(prospective_documents)
    validation["catalogue"] = validate_catalogue(catalogue)
    if not validation["valid"] or not validation["catalogue"]["valid"]:
        atomic_write_json(VALIDATION_REPORT_PATH, validation)
        raise SystemExit(f"Validation failed; indexing was not started: {validation['errors'][:5]}")
    index_args = argparse.Namespace(dry_run=args.dry_run)
    index_report = command_index(index_args, documents_override=prospective_documents)
    result = {"collection": collection_report, "index": index_report}
    if not args.dry_run:
        result["summary"] = command_report(argparse.Namespace())
    return result


def command_report(_args: argparse.Namespace) -> dict[str, Any]:
    _raw, collected, catalogue = load_datasets()
    settings = Settings()
    indexed_temple_ids: set[str] = set()
    indexed_document_ids: set[str] = set()
    try:
        from app.sqlite_compat import ensure_supported_sqlite
        ensure_supported_sqlite()
        import chromadb
        client = chromadb.PersistentClient(path=settings.chroma_persist_dir, settings=chromadb.Settings(anonymized_telemetry=False))
        try:
            collection = client.get_collection(name=settings.collection_name)
            indexed_count = collection.count()
            offset = 0
            while offset < indexed_count:
                batch = collection.get(limit=1000, offset=offset, include=["metadatas"])
                for metadata in batch.get("metadatas", []):
                    if not isinstance(metadata, dict):
                        continue
                    if isinstance(metadata.get("temple_id"), str):
                        indexed_temple_ids.add(metadata["temple_id"])
                    if isinstance(metadata.get("document_id"), str):
                        indexed_document_ids.add(metadata["document_id"])
                offset += len(batch.get("ids", []))
                if not batch.get("ids"):
                    break
        except Exception:
            indexed_count = 0
    except Exception as exc:
        logging.getLogger("temple_heritage.ingestion").exception("Could not read index count")
        indexed_count = None
        index_error = str(exc)
    else:
        index_error = None
    registry = _read_json(REGISTRY_PATH, {"sources": []})
    report = summarize_report(catalogue, merge_documents(_raw, collected), indexed_count or 0, registry.get("sources", []))
    catalogue_ids = {item.get("id") for item in catalogue if isinstance(item, dict)}
    report["indexed_unique_catalogue_temple_ids"] = len(indexed_temple_ids & catalogue_ids) if index_error is None else None
    report["indexed_unique_document_ids"] = len(indexed_document_ids) if index_error is None else None
    candidates = _read_json(DATA_DIR / "catalogue_candidates.json", [])
    report["catalogue_candidates_pending_review"] = len(candidates) if isinstance(candidates, list) else None
    last_collection = _read_json(COLLECTION_REPORT_PATH, None)
    if last_collection is None:
        last_collection = {
            "collected_at": None,
            "run_recorded": False,
            "source_urls": {"attempted": 0, "succeeded": 0, "failed": 0, "skipped": 0},
            "documents": {"new": 0, "updated": 0, "unchanged": 0, "duplicates": 0, "skipped_documents": 0},
            "sources": [
                {
                    "source_id": source.get("id"),
                    "status": "disabled" if not source.get("enabled") else "terms_review_required" if source.get("terms_review_status") != "approved" else "not_run",
                    "last_successful_collection": source.get("last_successful_collection"),
                }
                for source in registry.get("sources", []) if isinstance(source, dict)
            ],
        }
    report["last_collection"] = last_collection
    report["last_index"] = _read_json(INDEX_REPORT_PATH, None)
    report["index_count_error"] = index_error
    _persist_report(REPORT_PATH, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect, validate, and index trusted temple and heritage sources.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    collect = subparsers.add_parser("collect", help="Fetch explicitly configured public pages")
    collect.add_argument("--source", help="Only collect one configured source ID")
    collect.add_argument("--dry-run", action="store_true", help="Fetch and report without writing collection files")
    collect.set_defaults(handler=command_collect)
    validate = subparsers.add_parser("validate", help="Validate curated and collected documents")
    validate.add_argument("--dry-run", action="store_true", help="Do not write the validation report")
    validate.set_defaults(handler=command_validate)
    index = subparsers.add_parser("index", help="Upsert validated source documents into ChromaDB")
    index.add_argument("--dry-run", action="store_true", help="Report chunk count without embedding or changing ChromaDB")
    index.set_defaults(handler=command_index)
    run = subparsers.add_parser("run", help="Collect, validate, then index")
    run.add_argument("--dry-run", action="store_true", help="Collect and validate without writing files or ChromaDB")
    run.set_defaults(handler=command_run)
    report = subparsers.add_parser("report", help="Summarize catalogue, documents, source history, and index")
    report.set_defaults(handler=command_report)
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.handler(args)
    except (ValueError, OSError, RuntimeError) as exc:
        logging.getLogger("temple_heritage.ingestion").error("Ingestion command failed: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
