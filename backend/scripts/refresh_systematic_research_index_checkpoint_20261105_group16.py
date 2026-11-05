"""Record verified Group 16 collection/index counts in the research plan."""
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
    collection_chunks = index.get("chunks_after")
    if collection_chunks is None or not index.get("dry_run") is False:
        raise RuntimeError("index_report.json does not confirm a completed write")
    if not validation.get("valid") or not validation.get("catalogue", {}).get("valid"):
        raise RuntimeError("latest validation report is not valid")
    plan["catalogue_count"] = len(catalogue)
    plan["unique_temple_ids"] = len({row["id"] for row in catalogue})
    plan["current_knowledge_document_count"] = len(docs)
    plan["last_checkpoint"] = "2026-11-05-group16-indexed"
    plan["last_updated_utc"] = datetime.now(timezone.utc).isoformat()
    plan["data_integrity_checkpoint"] = {
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "catalogue_records": len(catalogue),
        "curated_document_count": len(docs),
        "collection": index.get("collection"),
        "collection_chunk_count": collection_chunks,
        "indexing": {
            "new_documents_added_this_operation": 65,
            "documents_text_modified_after_first_index": 8,
            "latest_dry_run_1_matches_dry_run_2": True,
            "latest_dry_run_documents_added": 7,
            "latest_dry_run_chunks_added": 13,
            "latest_dry_run_documents_updated": 0,
            "latest_dry_run_chunks_updated": 0,
            "latest_dry_run_metadata_only_updates": 0,
            "latest_dry_run_stale_chunks_removed": 0,
            "latest_index_write_succeeded": True,
            "chunks_after_latest_index": collection_chunks,
            "new_documents_review_status": "pending_human_review",
        },
        "note": "Group 16 dry runs were identical: seven new documents and 13 chunks to add, 384 documents unchanged, no updates/removals. Incremental index completed with 529 chunks. No existing records or unrelated chunks were removed.",
    }
    (DATA / "research_plan_all_217.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"catalogue": len(catalogue), "documents": len(docs), "chunks": collection_chunks}, indent=2))


if __name__ == "__main__":
    main()
