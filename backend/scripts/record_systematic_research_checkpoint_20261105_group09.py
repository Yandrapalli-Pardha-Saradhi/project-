"""Record manually inspected Sivasagar district administration pages."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
DOCS_PATH = DATA / "raw" / "temple_sources.json"
CATALOGUE_PATH = DATA / "catalogue.json"
PLAN_PATH = DATA / "research_plan_all_217.json"
ACCESS_DATE = "2026-11-05"
COLLECTED_AT = datetime.now(timezone.utc).isoformat()

SIVASAGAR_URL = "https://sivasagar.assam.gov.in/index.php/tourist-place-detail/275"
RANGANATH_URL = "https://sivasagar.assam.gov.in/tourist-place-detail/331"

ITEMS = [
    {
        "temple_id": "asi_assam_53f3d143b7f21899",
        "id_suffix": "sivasagar_siva_doul_district_administration_history_claim_conflict",
        "topic": "history_architecture_religious_cultural_significance_festivals_heritage_conservation",
        "title": "Siva Doul, Sivasagar: district administration account and attribution conflict",
        "url": SIVASAGAR_URL,
        "source_title": "Sivasagar Tank and Temples",
        "publication_date": "2026-09-30",
        "text": (
            "The Sivasagar district administration describes Siva Doul as one of three temples beside Sivasagar Tank in the centre of Sivasagar town. "
            "Its page contains conflicting construction attributions: one sentence says Shiva Doul was built by Queen Phuleswari in 1734, while a later passage says Siva Doul was constructed in 1734 by Queen Ambika, also called Madambika, wife of Swargadeo Siva Singha. "
            "The page does not reconcile these names, so the attribution needs independent review. The same account reports a golden finial (koloshi) eight feet high and gives the temple's height as 180 feet and breadth as 195 feet; these measurements are retained as claims of this page, not independently verified measurements. It also describes rare sculptures and says daily worship continues. "
            "The page links the Sivasagar temple group to an annual International Shiva Festival in March, but does not document temple-specific festival rites. It gives no current visitor hours or entry fee. Source page last updated 30 September 2026; accessed 5 November 2026."
        ),
    },
    {
        "temple_id": "asi_assam_087d550e6d805059",
        "id_suffix": "sivasagar_vishnu_doul_district_administration_group_history",
        "topic": "history_religious_cultural_significance_festivals",
        "title": "Vishnu Doul, Sivasagar: district administration account",
        "url": SIVASAGAR_URL,
        "source_title": "Sivasagar Tank and Temples",
        "publication_date": "2026-09-30",
        "text": (
            "The Sivasagar district administration identifies Vishnu Doul as one of the trio of Shiva, Vishnu and Devi temples beside Sivasagar Tank in Sivasagar town. It states that Vishnu Doul and Devi Doul were constructed in 1734 by Queen Ambika, also called Madambika, wife of Swargadeo Siva Singha, and says daily worship continues in both. The page does not describe Vishnu Doul's architectural plan, presiding icon, individual rituals or festival calendar. It mentions an annual International Shiva Festival in March in its account of the temple group, without specifying rites at Vishnu Doul. No current opening hours or admission fee are stated. Source page last updated 30 September 2026; accessed 5 November 2026."
        ),
    },
    {
        "temple_id": "asi_assam_6324da2158eb30bc",
        "id_suffix": "sivasagar_devi_doul_district_administration_group_history",
        "topic": "history_religious_cultural_significance_festivals",
        "title": "Devi Doul, Sivasagar: district administration account",
        "url": SIVASAGAR_URL,
        "source_title": "Sivasagar Tank and Temples",
        "publication_date": "2026-09-30",
        "text": (
            "The Sivasagar district administration identifies Devi Doul as one of the trio of Shiva, Vishnu and Devi temples beside Sivasagar Tank in Sivasagar town. It states that Vishnu Doul and Devi Doul were constructed in 1734 by Queen Ambika, also called Madambika, wife of Swargadeo Siva Singha, and says daily worship continues in both. Although the page calls this shrine Devi Doul, it does not identify its presiding deity more specifically or describe its architecture, individual rituals or festival calendar. It mentions an annual International Shiva Festival in March in its account of the temple group, without specifying rites at Devi Doul. No current opening hours or admission fee are stated. Source page last updated 30 September 2026; accessed 5 November 2026."
        ),
    },
    {
        "temple_id": "asi_assam_888093ddb8ea0098",
        "id_suffix": "joysagar_ranganath_doul_district_administration_history_architecture_protection",
        "topic": "history_architecture_religious_cultural_significance_heritage_conservation_visitor_information",
        "title": "Ranganath Doul at Joysagar: district administration history and site description",
        "url": RANGANATH_URL,
        "source_title": "Ranganath Temple and Fakua Doul",
        "publication_date": "2026-10-22",
        "text": (
            "The Sivasagar district administration identifies Ranganath Doul as a Shiva temple near the main gateway from Joysagar Tank to Talatal Ghar and says Swargadeo Rudra Singha built it in 1703 for worship of Shiva. The page states that daily worship continues and that the temple is a protected site under the Archaeological Survey of India. These are the page's claims; it does not provide a protection notification number or conservation history. The page's architecture and dimensions describe the separately named Fakuwa Doul, so those features are not attributed here to Ranganath Doul. The page places the two structures about four kilometres west of central Sivasagar town, but gives no temple-specific current hours or entry fee. Source page last updated 22 October 2026; accessed 5 November 2026."
        ),
    },
]


def make_doc(item: dict, catalogue_by_id: dict) -> dict:
    temple = catalogue_by_id[item["temple_id"]]
    document_id = "systematic_research_20261105_" + item["id_suffix"]
    text = " ".join(item["text"].split())
    return {
        "document_id": document_id,
        "temple_id": temple["id"],
        "temple_name": temple["canonical_name"],
        "state": temple["state"],
        "district": temple["district"],
        "topic": item["topic"],
        "title": item["title"],
        "source_title": item["source_title"],
        "source_url": item["url"],
        "publisher": "Sivasagar District Administration, Government of Assam",
        "source_type": "official_district_tourism",
        "language": "en",
        "publication_date": item["publication_date"],
        "retrieval_date": ACCESS_DATE,
        "collection_timestamp": COLLECTED_AT,
        "content_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "verification_status": "source_review_pending",
        "review_status": "pending_human_review",
        "is_paraphrase": True,
        "text": text,
    }


def main() -> None:
    docs = json.loads(DOCS_PATH.read_text(encoding="utf-8"))
    catalogue = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    catalogue_by_id = {row["id"]: row for row in catalogue}
    existing_ids = {row.get("document_id") for row in docs}
    added = []
    for item in ITEMS:
        doc = make_doc(item, catalogue_by_id)
        if doc["document_id"] not in existing_ids:
            docs.append(doc)
            added.append(doc)
        temple = catalogue_by_id[item["temple_id"]]
        if doc["document_id"] not in temple.setdefault("document_ids", []):
            temple["document_ids"].append(doc["document_id"])

    plan_by_id = {row["temple_id"]: row for row in plan["temples"]}
    for item in ITEMS:
        row = plan_by_id[item["temple_id"]]
        if item["url"] not in row.setdefault("sources_inspected", []):
            row["sources_inspected"].append(item["url"])
        if item["url"] not in row.setdefault("previously_inspected_source_urls", []):
            row["previously_inspected_source_urls"].append(item["url"])
        row["research_status"] = "enriched"
        notes = row.setdefault("research_notes", [])
        if isinstance(notes, str):
            notes = [notes] if notes else []
            row["research_notes"] = notes
        notes.append("District administration source page inspected in Group 09; document added with claims and gaps bounded to the page. Sivadol attribution conflict preserved.")
        row["documents_added"] = sorted(set(row.get("documents_added", [])) | {d["document_id"] for d in added if d["temple_id"] == item["temple_id"]})
        row["last_completed_checkpoint"] = "2026-11-05-group09"
        row["page_evidence_categories"] = sorted(set(row.get("page_evidence_categories", [])) | {"historical_background", "religious_cultural_significance"})
        row["remaining_gaps"] = sorted(set(row.get("remaining_gaps", [])) | {"architecture", "festivals_traditions", "inscriptions_historical_evidence", "heritage_conservation", "visitor_information"})

    urls = {
        SIVASAGAR_URL: {
            "source_url": SIVASAGAR_URL,
            "source_title": "Sivasagar Tank and Temples",
            "publisher": "Sivasagar District Administration, Government of Assam",
            "source_type": "official_district_tourism",
            "document_ids": [d["document_id"] for d in docs if d.get("source_url") == SIVASAGAR_URL],
            "temple_ids_with_cited_documents": ["asi_assam_53f3d143b7f21899", "asi_assam_087d550e6d805059", "asi_assam_6324da2158eb30bc"],
            "topics_in_cited_documents": ["history_architecture_religious_cultural_significance_festivals"],
            "page_inspected_for_temple_ids": ["asi_assam_53f3d143b7f21899", "asi_assam_087d550e6d805059", "asi_assam_6324da2158eb30bc"],
            "page_inspection_status": "manually_opened_and_read_2026-11-05",
        },
        RANGANATH_URL: {
            "source_url": RANGANATH_URL,
            "source_title": "Ranganath Temple and Fakua Doul",
            "publisher": "Sivasagar District Administration, Government of Assam",
            "source_type": "official_district_tourism",
            "document_ids": [d["document_id"] for d in docs if d.get("source_url") == RANGANATH_URL],
            "temple_ids_with_cited_documents": ["asi_assam_888093ddb8ea0098"],
            "topics_in_cited_documents": ["history_architecture_religious_cultural_significance_heritage_conservation"],
            "page_inspected_for_temple_ids": ["asi_assam_888093ddb8ea0098"],
            "page_inspection_status": "manually_opened_and_read_2026-11-05",
        },
    }
    sources = plan.setdefault("source_reuse_index", {}).setdefault("sources", [])
    by_url = {entry.get("source_url"): entry for entry in sources}
    for url, data in urls.items():
        if url in by_url:
            by_url[url].update(data)
        else:
            sources.append(data)
    checks = plan.setdefault("source_checks_this_operation", [])
    for check in [
        {"source_title": "Sivasagar Tank and Temples", "source_url": SIVASAGAR_URL,
         "publisher": "Sivasagar District Administration, Government of Assam", "source_type": "official_district_tourism",
         "publication_date": "2026-09-30", "accessed_date": ACCESS_DATE,
         "linked_temple_ids": ["asi_assam_53f3d143b7f21899", "asi_assam_087d550e6d805059", "asi_assam_6324da2158eb30bc"],
         "categories_with_relevant_source_content": ["historical_background", "architecture", "religious_cultural_significance", "festivals_traditions"],
         "inspection_method": "Opened the Sivasagar District Administration page and read its Sivasagar Tank and Temples section (web lines 71-80).",
         "note": "The page contains conflicting 1734 Siva Doul patron attributions; conflict preserved. It does not establish temple-specific visitor hours or entry fees."},
        {"source_title": "Ranganath Temple and Fakua Doul", "source_url": RANGANATH_URL,
         "publisher": "Sivasagar District Administration, Government of Assam", "source_type": "official_district_tourism",
         "publication_date": "2026-10-22", "accessed_date": ACCESS_DATE,
         "linked_temple_ids": ["asi_assam_888093ddb8ea0098"],
         "categories_with_relevant_source_content": ["historical_background", "religious_cultural_significance", "heritage_conservation", "visitor_information"],
         "inspection_method": "Opened and read the named Ranganath Doul section (web lines 71-83).",
         "note": "Fakuwa Doul architecture and local burial-mound belief were kept separate from Ranganath Doul."},
    ]:
        identity = (check["source_url"], tuple(check["linked_temple_ids"]))
        if not any((x.get("source_url"), tuple(x.get("linked_temple_ids", []))) == identity for x in checks):
            checks.append(check)
    plan["source_reuse_index"]["source_url_count"] = len(sources)
    plan["source_reuse_index"]["actually_inspected_url_count"] = sum(bool(entry.get("page_inspected_for_temple_ids")) for entry in sources)

    DOCS_PATH.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CATALOGUE_PATH.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    PLAN_PATH.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"catalogue": len(catalogue), "documents": len(docs), "added": [d["document_id"] for d in added], "new_document_count": len(added)}, indent=2))


if __name__ == "__main__":
    main()
