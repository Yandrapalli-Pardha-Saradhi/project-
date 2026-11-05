"""Record the named Negheriting Sivadol section of ASI's 2010-11 report."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
TEMPLE_ID = "asi_assam_dbf0ecb97451eb87"
DOC_ID = "systematic_research_20261105_negheriting_sivadol_asi_2010_11_conservation"
URL = "https://asiguwahaticircle.gov.in/paw.pdf"


def main() -> None:
    docs_path = DATA / "raw" / "temple_sources.json"
    catalogue_path = DATA / "catalogue.json"
    plan_path = DATA / "research_plan_all_217.json"
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    temple = next(row for row in catalogue if row["id"] == TEMPLE_ID)
    text = (
        "The Archaeological Survey of India (ASI), Guwahati Circle report covering activities during 2010–2011 names Sivadol at Negheriting, Golaghat district, Assam. It describes a panchayatana temple complex with a main temple and four miniature shrines at the corners. The report records lime-concrete finishing to the mandapa, lime-surkhi plastering to the monument, and restoration of the ancient steps leading to the temple. These are conservation actions reported for 2010–2011 and do not establish the site's current condition. The report does not give a construction date, festival schedule, or present visitor timings. Accessed 5 November 2026; source section inspected at extracted PDF lines 142–178."
    )
    text = " ".join(text.split())
    doc = {
        "document_id": DOC_ID,
        "temple_id": TEMPLE_ID,
        "temple_name": temple["canonical_name"],
        "state": temple["state"],
        "district": temple["district"],
        "topic": "architecture_heritage_conservation",
        "title": "Sivadol at Negheriting: ASI report on temple complex and 2010–11 conservation",
        "source_title": "Activities of Archaeological Survey of India, Guwahati Circle during 2010 & 2011",
        "source_url": URL,
        "publisher": "Archaeological Survey of India, Guwahati Circle",
        "source_type": "official_asi_circle_conservation_report",
        "language": "en",
        "publication_date": None,
        "retrieval_date": "2026-11-05",
        "collection_timestamp": datetime.now(timezone.utc).isoformat(),
        "content_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "verification_status": "source_review_pending",
        "review_status": "pending_human_review",
        "is_paraphrase": True,
        "text": text,
    }
    existing = next((item for item in docs if item.get("document_id") == DOC_ID), None)
    if existing is None:
        docs.append(doc)
    elif existing.get("content_hash") != doc["content_hash"]:
        existing.update({"text": text, "content_hash": doc["content_hash"]})
    if DOC_ID not in temple.setdefault("document_ids", []):
        temple["document_ids"].append(DOC_ID)
    row = next(item for item in plan["temples"] if item["temple_id"] == TEMPLE_ID)
    for field in ("sources_inspected", "previously_inspected_source_urls"):
        if URL not in row.setdefault(field, []):
            row[field].append(URL)
    row["research_status"] = "enriched"
    row["last_completed_checkpoint"] = "2026-11-05-group14"
    row["page_evidence_categories"] = sorted(set(row.get("page_evidence_categories", [])) | {"architecture", "heritage_conservation"})
    notes = row.setdefault("research_notes", [])
    if isinstance(notes, str):
        notes = [notes] if notes else []
        row["research_notes"] = notes
    note = "ASI Guwahati Circle 2010–2011 report's named Negheriting Sivadol passage was inspected; its conservation account is historical, not current condition."
    if note not in notes:
        notes.append(note)
    checks = plan.setdefault("source_checks_this_operation", [])
    check = next((item for item in checks if item.get("source_url") == URL), None)
    if check:
        check["linked_temple_ids"] = sorted(set(check.get("linked_temple_ids", [])) | {TEMPLE_ID})
        check["categories_with_relevant_source_content"] = sorted(set(check.get("categories_with_relevant_source_content", [])) | {"architecture", "heritage_conservation"})
    else:
        checks.append({
            "source_title": doc["source_title"], "source_url": URL, "publisher": doc["publisher"],
            "source_type": doc["source_type"], "publication_date": None, "accessed_date": "2026-11-05",
            "linked_temple_ids": [TEMPLE_ID], "categories_with_relevant_source_content": ["architecture", "heritage_conservation"],
            "inspection_method": "Opened ASI Guwahati Circle activity-report PDF and read the named Negheriting Sivadol section.",
            "note": "Report covers conservation actions in 2010–2011 and is not evidence of current condition.",
        })
    docs_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    catalogue_path.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"catalogue": len(catalogue), "documents": len(docs), "document_id": DOC_ID}, indent=2))


if __name__ == "__main__":
    main()
