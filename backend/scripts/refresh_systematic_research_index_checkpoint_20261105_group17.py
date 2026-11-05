"""Record Group 17's verified validation and ChromaDB index results."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


def read(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def main() -> None:
    plan = read("research_plan_all_217.json")
    catalogue = read("catalogue.json")
    docs = read("raw/temple_sources.json")
    index = read("index_report.json")
    validation = read("validation_report.json")
    chunks = index.get("chunks_after")
    if index.get("dry_run") is not False or chunks is None:
        raise RuntimeError("No successful non-dry-run index report is available")
    if not validation.get("valid") or not validation.get("catalogue", {}).get("valid"):
        raise RuntimeError("Catalogue/document validation did not pass")
    plan["catalogue_count"] = len(catalogue)
    plan["unique_temple_ids"] = len({r["id"] for r in catalogue})
    plan["current_knowledge_document_count"] = len(docs)
    plan["last_checkpoint"] = "2026-11-05-group17-indexed"
    plan["last_updated_utc"] = datetime.now(timezone.utc).isoformat()
    plan["data_integrity_checkpoint"] = {
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "catalogue_records": len(catalogue),
        "curated_document_count": len(docs),
        "collection": index.get("collection"),
        "collection_chunk_count": chunks,
        "indexing": {
            "new_documents_added_this_operation": 69,
            "documents_text_modified_after_their_first_index": 8,
            "latest_dry_run_1_matches_dry_run_2": True,
            "latest_dry_run_documents_added": 1,
            "latest_dry_run_chunks_added": 1,
            "latest_dry_run_documents_updated": 0,
            "latest_dry_run_chunks_updated": 0,
            "latest_dry_run_metadata_only_updates": 0,
            "latest_dry_run_stale_chunks_removed": 0,
            "latest_index_write_succeeded": True,
            "chunks_before_latest_index": 536,
            "chunks_after_latest_index": chunks,
            "new_documents_review_status": "pending_human_review",
        },
        "note": "Group 17 comprised two safe incremental writes. The first pair of dry runs matched at three documents/seven chunks, then that subset was indexed (collection 529 to 536). The later location document had two matching dry runs at one document/one chunk and was indexed (536 to 537). No updates or removals occurred.",
    }
    (DATA / "research_plan_all_217.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"catalogue": len(catalogue), "documents": len(docs), "chunks": chunks}, indent=2))


if __name__ == "__main__":
    main()
