"""Persist indexing/checkpoint facts for the resumable research queue."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "data" / "research_plan_all_217.json"


def main() -> None:
    plan = json.loads(PATH.read_text(encoding="utf-8"))
    plan["data_integrity_checkpoint"] = {
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "catalogue_records": 217,
        "curated_document_count": 384,
        "collection": "temple_heritage",
        "collection_chunk_count": 516,
        "indexing": {
            "new_documents_added_this_operation": 58,
            "documents_text_modified_after_first_index": 9,
            "latest_dry_run_1_matches_dry_run_2": True,
            "latest_dry_run_documents_updated": 1,
            "latest_dry_run_documents_added": 0,
            "latest_dry_run_chunks_added": 0,
            "latest_dry_run_chunks_updated": 2,
            "latest_dry_run_metadata_only_updates": 3,
            "latest_dry_run_stale_chunks_removed": 0,
            "latest_index_write_succeeded": True,
            "chunks_after_latest_index": 516,
            "new_documents_review_status": "pending_human_review",
        },
        "updated_document_ids": [
            "systematic_research_20261105_kambaduru_mallikarjuna_asi_conservation_1956",
            "systematic_research_20261105_sivasagar_sivadol_assam_tourism_context",
            "systematic_research_20261105_bharmour_ganesh_chaurasi_asi_heritage_context",
            "systematic_research_20261105_bharmour_lakshana_devi_chaurasi_asi_heritage_context",
            "systematic_research_20261105_bharmour_manimahesh_chaurasi_asi_heritage_context",
            "systematic_research_20261105_bharmour_narsingh_chaurasi_asi_heritage_context",
            "systematic_research_20261105_chamba_lakshmi_narayan_tourism_architecture_patronage",
            "systematic_research_20261105_joysagar_devidol_devighar_identity_location",
        ],
        "note": "Across this operation, 58 new documents were added and nine existing documents were text-updated after indexing to correct source caveats or remove negative-evidence wording. Three obsolete chunks were removed only as stale versions of seven earlier modified documents. Group 10 dry runs matched: three new documents/six chunks; its later wording refinement matched at one document/two chunks updated, with no deletions. Group 12 added two documents/four chunks; Group 13 added six documents/12 chunks; Group 14 added one document/two chunks; Group 15 added four documents/17 chunks. A previously mislabelled title and publisher for one Belavadi source record were corrected as metadata-only updates across four chunks; subsequent caveat refinements in the same new document updated at most two chunks and three metadata records without changing total count. The collection is now 516 chunks; all new documents remain pending human review.",
    }
    PATH.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Recorded current document/index checkpoint.")


if __name__ == "__main__":
    main()
