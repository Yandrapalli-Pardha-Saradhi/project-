"""Attach existing source-document provenance to the all-temple research queue."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    plan_path = DATA / "research_plan_all_217.json"
    plan = read(plan_path)
    docs = read(DATA / "raw" / "temple_sources.json")
    manifests = sorted(DATA.glob("enrichment_manifest_batch_*.json"))
    batch_by_temple: dict[str, list[str]] = defaultdict(list)
    for path in manifests:
        batch_id = path.stem.replace("enrichment_manifest_", "")
        for row in read(path).get("temples", []):
            if row.get("temple_id"):
                batch_by_temple[row["temple_id"]].append(batch_id)

    by_temple: dict[str, list[dict]] = defaultdict(list)
    for doc in docs:
        temple_id = doc.get("temple_id")
        url = str(doc.get("source_url") or "")
        document_id = str(doc.get("document_id") or "")
        source_type = str(doc.get("source_type") or "")
        source_title = str(doc.get("source_title") or "")
        inventory = (
            document_id.startswith("asi_inventory_")
            or "inventory" in source_type.casefold()
            or "centrally protected monuments/sites" in source_title.casefold()
        )
        # The all217_research_* set is the prior checkpoint explicitly resumed
        # by this task and counts as existing provenance. Only this resumed
        # checkpoint's resume_research_* documents are new here.
        is_this_operation = document_id.startswith("resume_research_20261105_")
        if temple_id and url.startswith(("https://", "http://")) and not inventory and not is_this_operation:
            by_temple[temple_id].append({
                "document_id": document_id,
                "title": doc.get("title") or doc.get("source_title"),
                "topic": doc.get("topic"),
                "source_title": doc.get("source_title"),
                "source_url": url,
                "source_type": doc.get("source_type"),
                "review_status": doc.get("review_status") or doc.get("verification_status"),
            })

    prior_source_temple_ids = set(by_temple)
    prior_checkpoint_docs: dict[str, list[str]] = defaultdict(list)
    for doc in docs:
        document_id = str(doc.get("document_id") or "")
        if document_id.startswith("all217_research_20261105_") and doc.get("temple_id"):
            prior_checkpoint_docs[doc["temple_id"]].append(document_id)
    current_source_temple_ids = {
        row["temple_id"] for row in plan["temples"] if row.get("sources_inspected")
    }
    for row in plan["temples"]:
        temple_id = row["temple_id"]
        existing = sorted(by_temple.get(temple_id, []), key=lambda x: x["document_id"])
        row["prior_source_attributed_documents"] = existing
        row["prior_source_attributed_document_count"] = len(existing)
        row["prior_source_topics"] = sorted({str(item["topic"]) for item in existing if item.get("topic")})
        row["prior_enrichment_manifest_batches"] = sorted(set(batch_by_temple.get(temple_id, [])))
        row["prior_source_provenance_status"] = (
            "source_attributed_documents_present_pending_claim_review" if existing
            else "no_temple_specific_noninventory_source_document_found"
        )
        # Preserve the current-operation page-check status separately from
        # prior source documents; a URL in the corpus is not proof of fresh inspection.
        if row.get("sources_inspected"):
            row["research_status"] = "current_operation_pages_inspected_partial_categories"
        elif existing:
            row["research_status"] = "prior_source_attributed_material_present_gap_review_required"
        else:
            row["research_status"] = "no_noninventory_temple_source_found_research_pending"

    plan["prior_source_attributed_temple_count"] = len(prior_source_temple_ids)
    plan["prior_source_attributed_temple_ids"] = sorted(prior_source_temple_ids)
    plan["prior_source_attributed_but_not_opened_this_operation_count"] = len(prior_source_temple_ids - current_source_temple_ids)
    plan["temples_without_prior_noninventory_source_document_count"] = len(plan["temples"]) - len(prior_source_temple_ids)
    plan["temples_without_prior_noninventory_source_document_ids"] = sorted(
        row["temple_id"] for row in plan["temples"] if row["temple_id"] not in prior_source_temple_ids
    )
    plan["prior_source_provenance_note"] = (
        "Existing non-inventory documents and their URLs are recorded per temple. These are source-attributed leads from earlier work, "
        "not independent proof that each page was opened or each factual claim was verified. Do not repeat work where existing evidence is adequate; "
        "review remaining topic gaps and source content."
    )
    plan["previous_all_temple_checkpoint"] = {
        "temple_count": len(prior_checkpoint_docs),
        "document_count": sum(len(ids) for ids in prior_checkpoint_docs.values()),
        "temples": [
            {"temple_id": temple_id, "name": next(row["canonical_name"] for row in plan["temples"] if row["temple_id"] == temple_id),
             "document_ids": sorted(ids)}
            for temple_id, ids in sorted(prior_checkpoint_docs.items())
        ],
    }
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "catalogue_records": len(plan["temples"]),
        "prior_source_attributed_temple_count": len(prior_source_temple_ids),
        "prior_source_docs_not_reopened_this_operation": plan["prior_source_attributed_but_not_opened_this_operation_count"],
        "without_prior_noninventory_source_document": plan["temples_without_prior_noninventory_source_document_count"],
        "current_operation_pages_inspected": len(current_source_temple_ids),
    }, indent=2))


if __name__ == "__main__":
    main()
