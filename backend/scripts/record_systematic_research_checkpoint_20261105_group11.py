"""Record a manually inspected Gaurisagar temple-specific source."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
URL = "https://sivasagar.assam.gov.in/tourist-place-detail/333"
TEMPLE_ID = "asi_assam_d296790c660bb3b9"
DOC_ID = "systematic_research_20261105_gaurisagar_devidol_sandstone_sculptures"


def main() -> None:
    docs_path = DATA / "raw" / "temple_sources.json"
    catalogue_path = DATA / "catalogue.json"
    plan_path = DATA / "research_plan_all_217.json"
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    temple = next(row for row in catalogue if row["id"] == TEMPLE_ID)
    text = (
        "The Sivasagar district administration's Gaurisagar Tank and Doul page says the tank covers 400 bighas and was constructed by Queen Phuleswari, with three temples on its north bank. It specifically describes Devi Doul as decorated with numerous sandstone sculptures. This page does not date the Devi Doul temple itself or identify individual sculptural figures, and the tank's construction attribution is not treated as a temple construction date. The page was last updated 29 October 2026 and was accessed 5 November 2026."
    )
    text = " ".join(text.split())
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    existing = next((doc for doc in docs if doc.get("document_id") == DOC_ID), None)
    document = {
        "document_id": DOC_ID,
        "temple_id": TEMPLE_ID,
        "temple_name": temple["canonical_name"],
        "state": temple["state"],
        "district": temple["district"],
        "topic": "architecture_history",
        "title": "Devidol, Gaurisagar: district administration description of sculpture",
        "source_title": "Gaurisagar Tank and Doul",
        "source_url": URL,
        "publisher": "Sivasagar District Administration, Government of Assam",
        "source_type": "official_district_tourism",
        "language": "en",
        "publication_date": "2026-10-29",
        "retrieval_date": "2026-11-05",
        "collection_timestamp": datetime.now(timezone.utc).isoformat(),
        "content_hash": digest,
        "verification_status": "source_review_pending",
        "review_status": "pending_human_review",
        "is_paraphrase": True,
        "text": text,
    }
    if existing is None:
        docs.append(document)
    elif existing.get("content_hash") != digest:
        existing.update({"text": text, "content_hash": digest})
    if DOC_ID not in temple.setdefault("document_ids", []):
        temple["document_ids"].append(DOC_ID)
    row = next(item for item in plan["temples"] if item["temple_id"] == TEMPLE_ID)
    for field in ("sources_inspected", "previously_inspected_source_urls"):
        if URL not in row.setdefault(field, []):
            row[field].append(URL)
    row["research_status"] = "enriched"
    row["last_completed_checkpoint"] = "2026-11-05-group11"
    row["page_evidence_categories"] = sorted(set(row.get("page_evidence_categories", [])) | {"architecture"})
    row["remaining_gaps"] = sorted(set(row.get("remaining_gaps", [])) | {"historical_background", "religious_cultural_significance", "festivals_traditions", "inscriptions_historical_evidence", "heritage_conservation", "visitor_information"})
    notes = row.setdefault("research_notes", [])
    if isinstance(notes, str):
        notes = [notes] if notes else []
        row["research_notes"] = notes
    note = "Official district page inspected via direct HTTP 200 request; only its specific statement about Devi Doul's sandstone sculptures was used. Tank patronage/date not assigned to the shrine."
    if note not in notes:
        notes.append(note)
    checks = plan.setdefault("source_checks_this_operation", [])
    check = {
        "source_title": "Gaurisagar Tank and Doul",
        "source_url": URL,
        "publisher": "Sivasagar District Administration, Government of Assam",
        "source_type": "official_district_tourism",
        "publication_date": "2026-10-29",
        "accessed_date": "2026-11-05",
        "linked_temple_ids": [TEMPLE_ID],
        "categories_with_relevant_source_content": ["architecture"],
        "inspection_method": "Direct HTTP request returned 200; actual page body was extracted and the named Gaurisagar section read.",
        "note": "Page distinguishes the tank from its three temples; only the expressly named Devi Doul sculpture statement is attributed to the temple.",
    }
    if not any(item.get("source_url") == URL and TEMPLE_ID in item.get("linked_temple_ids", []) for item in checks):
        checks.append(check)
    docs_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    catalogue_path.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"catalogue": len(catalogue), "documents": len(docs), "document_id": DOC_ID, "review_status": "pending_human_review"}, indent=2))


if __name__ == "__main__":
    main()
