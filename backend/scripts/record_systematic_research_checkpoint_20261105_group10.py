"""Record the manually inspected official Joysagar Tank and Temples page."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
DOCS_PATH = DATA / "raw" / "temple_sources.json"
CATALOGUE_PATH = DATA / "catalogue.json"
PLAN_PATH = DATA / "research_plan_all_217.json"
URL = "https://sivasagar.assam.gov.in/tourist-place-detail/329"
ACCESS_DATE = "2026-11-05"
COLLECTED_AT = datetime.now(timezone.utc).isoformat()

ITEMS = [
    {
        "temple_id": "asi_assam_fcd74543096308a5",
        "slug": "joysagar_sivadol_baidyanath_khar_doul_history",
        "title": "Sivadol at Joysagar: district administration history and names",
        "topic": "history_religious_cultural_significance",
        "text": "The Sivasagar district administration identifies the Joysagar Shiva Doul also as Baidyanath Shiva Doul or Khara Doul, and calls it the Major Doul on the northern side of Joysagar Tank. The page attributes its construction to Swargadeo Rudra Singha in 1696. This is the temple date stated by the administration; the same page separately dates the tank to 1707, and that tank date is not used as the shrine's date. The page does not describe the temple's plan, construction materials, inscriptions, festival schedule, or current visitor hours. Accessed 5 November 2026; page last updated 29 October 2026.",
    },
    {
        "temple_id": "asi_assam_80af7f930eb9cfb5",
        "slug": "joysagar_bishnudol_keshabrai_identity_location",
        "title": "Bishnudol at Joysagar: district administration identification",
        "topic": "architecture_religious_cultural_significance_visitor_information",
        "text": "The Sivasagar district administration identifies Joy Doul, also called Keshabrai Vishnu Doul, on the northern side of Joysagar Tank. It describes the temple as displaying art and culture associated with the Ahom-era structure, without naming specific features or providing an individual construction date. The page separately describes Joysagar Tank as having been excavated in 1707; it does not say that this was the temple's construction year. It gives the tank complex's direction and distance from central Sivasagar but no temple-specific hours, fees, inscriptions, or festival information. Accessed 5 November 2026; page last updated 29 October 2026.",
    },
    {
        "temple_id": "asi_assam_6f13d020bbaf4068",
        "slug": "joysagar_devidol_devighar_identity_location",
        "title": "Devidol at Joysagar: district administration identification",
        "topic": "religious_cultural_significance_visitor_information",
        "text": "The Sivasagar district administration identifies Devighar, also called Devaloya, at the north-western corner of Joysagar Tank and says it was constructed for worship of Devi Durga. The page does not provide a construction date or identify a patron. Its location note places the Joysagar Tank complex about four kilometres west of central Sivasagar; this is complex-level access context, not a temple-specific visitor guide. The source does not state current temple opening hours or fees. Accessed 5 November 2026; page last updated 29 October 2026.",
    },
]


def main() -> None:
    docs = json.loads(DOCS_PATH.read_text(encoding="utf-8"))
    catalogue = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    by_id = {row["id"]: row for row in catalogue}
    plan_by_id = {row["temple_id"]: row for row in plan["temples"]}
    by_document_id = {row.get("document_id"): row for row in docs}
    existing = set(by_document_id)
    added = []
    modified = []
    for item in ITEMS:
        temple = by_id[item["temple_id"]]
        document_id = f"systematic_research_20261105_{item['slug']}"
        text = " ".join(item["text"].split())
        doc = {
            "document_id": document_id,
            "temple_id": temple["id"],
            "temple_name": temple["canonical_name"],
            "state": temple["state"],
            "district": temple["district"],
            "topic": item["topic"],
            "title": item["title"],
            "source_title": "Joysagar Tank and Temples",
            "source_url": URL,
            "publisher": "Sivasagar District Administration, Government of Assam",
            "source_type": "official_district_tourism",
            "language": "en",
            "publication_date": "2026-10-29",
            "retrieval_date": ACCESS_DATE,
            "collection_timestamp": COLLECTED_AT,
            "content_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "verification_status": "source_review_pending",
            "review_status": "pending_human_review",
            "is_paraphrase": True,
            "text": text,
        }
        if document_id not in existing:
            docs.append(doc)
            added.append(doc)
        else:
            old = by_document_id[document_id]
            if old.get("text") != text or old.get("content_hash") != doc["content_hash"]:
                old["text"] = text
                old["content_hash"] = doc["content_hash"]
                modified.append(document_id)
        if document_id not in temple.setdefault("document_ids", []):
            temple["document_ids"].append(document_id)
        row = plan_by_id[item["temple_id"]]
        for key in ("sources_inspected", "previously_inspected_source_urls"):
            if URL not in row.setdefault(key, []):
                row[key].append(URL)
        row["research_status"] = "enriched"
        notes = row.setdefault("research_notes", [])
        if isinstance(notes, str):
            notes = [notes] if notes else []
            row["research_notes"] = notes
        note = "Joysagar Tank and Temples page inspected in Group 10; claims limited to the named Joysagar shrine and explicit location/date statements."
        if note not in notes:
            notes.append(note)
        row["documents_added"] = sorted(set(row.get("documents_added", [])) | {d["document_id"] for d in added if d["temple_id"] == item["temple_id"]})
        row["last_completed_checkpoint"] = "2026-11-05-group10"
        row["page_evidence_categories"] = sorted(set(row.get("page_evidence_categories", [])) | {"historical_background", "religious_cultural_significance"})
        row["remaining_gaps"] = sorted(set(row.get("remaining_gaps", [])) | {"architecture", "festivals_traditions", "inscriptions_historical_evidence", "heritage_conservation", "visitor_information"})

    sources = plan.setdefault("source_reuse_index", {}).setdefault("sources", [])
    source = next((s for s in sources if s.get("source_url") == URL), None)
    entry = {
        "source_url": URL,
        "source_title": "Joysagar Tank and Temples",
        "publisher": "Sivasagar District Administration, Government of Assam",
        "source_type": "official_district_tourism",
        "document_ids": [d["document_id"] for d in docs if d.get("source_url") == URL],
        "temple_ids_with_cited_documents": [item["temple_id"] for item in ITEMS],
        "topics_in_cited_documents": ["history_architecture_religious_cultural_significance_visitor_information"],
        "page_inspected_for_temple_ids": [item["temple_id"] for item in ITEMS],
        "page_inspection_status": "manually_opened_and_read_2026-11-05",
    }
    if source:
        source.update(entry)
    else:
        sources.append(entry)
    checks = plan.setdefault("source_checks_this_operation", [])
    check = {
        "source_title": "Joysagar Tank and Temples", "source_url": URL,
        "publisher": "Sivasagar District Administration, Government of Assam", "source_type": "official_district_tourism",
        "publication_date": "2026-10-29", "accessed_date": ACCESS_DATE,
        "linked_temple_ids": [item["temple_id"] for item in ITEMS],
        "categories_with_relevant_source_content": ["historical_background", "architecture", "religious_cultural_significance", "visitor_information"],
        "inspection_method": "Opened and read the Joysagar Tank and Temples page (web lines 71-78).",
        "note": "Temple names and reported positions were matched to Joysagar catalogue records. The tank's 1707 date was not assigned as a temple construction date; separate shrine claims are retained as the administration's statements.",
    }
    identity = (check["source_url"], tuple(check["linked_temple_ids"]))
    if not any((x.get("source_url"), tuple(x.get("linked_temple_ids", []))) == identity for x in checks):
        checks.append(check)
    plan["source_reuse_index"]["source_url_count"] = len(sources)
    plan["source_reuse_index"]["actually_inspected_url_count"] = sum(bool(s.get("page_inspected_for_temple_ids")) for s in sources)
    DOCS_PATH.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CATALOGUE_PATH.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    PLAN_PATH.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"catalogue": len(catalogue), "documents": len(docs), "added": [d["document_id"] for d in added], "modified": modified}, indent=2))


if __name__ == "__main__":
    main()
