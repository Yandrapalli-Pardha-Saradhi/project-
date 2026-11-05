"""Append only the manually inspected 2026-11-05 research checkpoint."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS_PATH = DATA / "raw" / "temple_sources.json"
CATALOGUE_PATH = DATA / "catalogue.json"
PLAN_PATH = DATA / "research_plan_all_217.json"
ACCESS_DATE = "2026-11-05"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_doc(document_id: str, temple_id: str, temple_name: str, state: str, district: str,
             topic: str, title: str, source_title: str, source_url: str, publisher: str,
             source_type: str, text: str, publication_date: str | None = None) -> dict:
    return {
        "document_id": document_id,
        "temple_id": temple_id,
        "temple_name": temple_name,
        "state": state,
        "district": district,
        "topic": topic,
        "title": title,
        "source_title": source_title,
        "source_url": source_url,
        "publisher": publisher,
        "source_type": source_type,
        "language": "en",
        "publication_date": publication_date,
        "retrieval_date": ACCESS_DATE,
        "collection_timestamp": datetime.now(timezone.utc).isoformat(),
        "content_hash": hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest(),
        "verification_status": "source_review_pending",
        "review_status": "pending_human_review",
        "is_paraphrase": True,
        "text": text,
    }


documents = [
    make_doc(
        "resume_research_20261105_jagannath_architecture_culture",
        "jagannath", "Jagannath Temple in Puri", "Odisha", "Puri",
        "history_architecture_religious_culture",
        "Shree Jagannath Temple: state tourism account of the complex and living traditions",
        "Shree Jagannath Temple", "https://odishatourism.gov.in/en/places/shree-jagannath-temple",
        "Department of Tourism, Government of Odisha", "official_state_tourism_page",
        "Odisha Tourism describes Shree Jagannath Temple as a 12th-century temple built by Anantavarman Chodaganga Deva in the Kalinga style. Its page identifies Jagannath, Balabhadra and Subhadra as the wooden deities and connects periodic renewal of the images with Nabakalebara, describing the interval as 12–19 years. It names the principal architectural components as the Vimana or sanctum, Jagamohan or assembly hall, Natyamandira or dance hall, Bhoga Mandapa or offering hall, and Singhadwara, and gives the shikhara height as 65 metres. The page also describes daily Mahaprasad preparation in earthen pots. These are claims of the state tourism page and remain pending source review; the page does not establish temple-specific inscriptions or conservation history.",
    ),
    make_doc(
        "resume_research_20261105_jagannath_ratha_jatra_2026",
        "jagannath", "Jagannath Temple in Puri", "Odisha", "Puri",
        "festivals_rituals",
        "Puri Ratha Jatra: rituals and the 2026 Odisha Tourism calendar",
        "Puri Ratha Jatra 2026 & Chariot Festival", "https://odishatourism.gov.in/en/ratha-jatra-2026",
        "Department of Tourism, Government of Odisha", "official_state_tourism_event_page",
        "Odisha Tourism's Ratha Jatra page describes the annual procession in which Jagannath, Balabhadra and Subhadra leave the Shree Mandir and travel along Bada Danda toward Gundicha Temple. It names Pahandi, Chhera Pahanra, Gundicha Jatra, Bahuda Jatra, Suna Besha and Niladri Bije, and says the deities stay at Gundicha Temple for seven days before the return journey. The page presents the account of the deities' illness after Deba Snana Purnima and Gundicha as an aunt's home as religious tradition, not as historical evidence. Its calendar is specifically for 2026: it lists Ratha Jatra on 16 July, Bahuda on 24 July and Niladri Bije on 27 July. These dates are an archived 2026 schedule, not a future timetable. The page does not supply temple-specific epigraphic evidence.",
        publication_date="2026 (event calendar)",
    ),
    make_doc(
        "resume_research_20261105_kashi_official_faq_visitor_rituals",
        "kashi_vishwanath", "Kashi Vishwanath Temple", "Uttar Pradesh", "Varanasi",
        "visitor_information_festivals_rituals",
        "Kashi Vishwanath Temple: official FAQ visitor timings and named observances",
        "FAQ — Shri Kashi Vishwanath Temple", "https://www.shrikashivishwanath.org/pdffile/FAQ_SHRI_KASHI_VISHWANTH_TEMPLE_2_0_pdf.pdf",
        "Shri Kashi Vishwanath Temple", "official_temple_administration_faq_pdf",
        "The temple administration FAQ PDF lists general temple opening hours as 03:00–23:00 and darshan windows as 04:00–11:00, 12:20–19:00 and 20:30–21:00. It lists Mangala Aarti at 03:00–04:00, Midday/Bhog Aarti at 11:15–12:20, Sapta-Rishi Aarti at 19:00–20:15 and Night/Shringar Aarti at 21:00–22:15. In its FAQ answer on functions and festivals, it names Rangbhari Ekadashi, Diwali, monthly Shivratri, Mahashivratri and the month of Kartik. The PDF also states that ordinary entry has no fee while special darshan has a charge; because these arrangements are time-sensitive, check the temple's current official portal before travel rather than relying on this document as a live notice. The PDF table of contents points to temple timing on page 4 and festivals on page 8. No publication date is stated in the inspected PDF text; accessed 2026-11-05.",
    ),
]

source_checks = [
    {
        "source_title": "Sri Meenakshi - Sundareswarar Temple",
        "source_url": "https://madurai.nic.in/tourist-place/sri-meenakshi-sundareswarar-temple/",
        "publisher": "Madurai District Administration, Government of Tamil Nadu",
        "source_type": "official_district_tourism_page",
        "publication_date": "2018-07-23 (page last updated)",
        "accessed_date": ACCESS_DATE,
        "inspection_method": "Opened and read page text; no automated collection.",
        "linked_temple_ids": ["meenakshi"],
        "categories_with_relevant_source_content": ["historical_background", "architecture", "religious_cultural_significance", "visitor_information"],
    },
    {
        "source_title": "Festivals and Events — Madurai District",
        "source_url": "https://madurai.nic.in/festivals-and-events/",
        "publisher": "Madurai District Administration, Government of Tamil Nadu",
        "source_type": "official_district_festival_page",
        "publication_date": "2018-07-23 (page last updated)",
        "accessed_date": ACCESS_DATE,
        "inspection_method": "Opened and read festival descriptions; legends retained as tradition, not historical fact.",
        "linked_temple_ids": ["meenakshi"],
        "categories_with_relevant_source_content": ["festivals_traditions"],
    },
    {
        "source_title": "Shree Kashi Vishvanath Temple",
        "source_url": "https://varanasi.nic.in/tourist-place/shri-kashi-vishwanath-temple/",
        "publisher": "Varanasi District Administration, Government of Uttar Pradesh",
        "source_type": "official_district_tourism_page",
        "publication_date": "2026-03-06 (page last updated)",
        "accessed_date": ACCESS_DATE,
        "inspection_method": "Opened and read page text; no automated collection.",
        "linked_temple_ids": ["kashi_vishwanath"],
        "categories_with_relevant_source_content": ["religious_cultural_significance", "visitor_information"],
    },
    {
        "source_title": "FAQ — Shri Kashi Vishwanath Temple",
        "source_url": "https://www.shrikashivishwanath.org/pdffile/FAQ_SHRI_KASHI_VISHWANTH_TEMPLE_2_0_pdf.pdf",
        "publisher": "Shri Kashi Vishwanath Temple",
        "source_type": "official_temple_administration_faq_pdf",
        "publication_date": None,
        "accessed_date": ACCESS_DATE,
        "pdf_page_references": [4, 8],
        "inspection_method": "Opened and read extracted PDF text; table of contents identifies timing on p.4 and festival FAQ on p.8.",
        "linked_temple_ids": ["kashi_vishwanath"],
        "categories_with_relevant_source_content": ["festivals_traditions", "visitor_information"],
    },
    {
        "source_title": "Shree Jagannath Temple",
        "source_url": "https://odishatourism.gov.in/en/places/shree-jagannath-temple",
        "publisher": "Department of Tourism, Government of Odisha",
        "source_type": "official_state_tourism_page",
        "publication_date": None,
        "accessed_date": ACCESS_DATE,
        "inspection_method": "Opened and read page text; no automated collection.",
        "linked_temple_ids": ["jagannath"],
        "categories_with_relevant_source_content": ["historical_background", "architecture", "religious_cultural_significance", "visitor_information"],
    },
    {
        "source_title": "Puri Ratha Jatra 2026 & Chariot Festival",
        "source_url": "https://odishatourism.gov.in/en/ratha-jatra-2026",
        "publisher": "Department of Tourism, Government of Odisha",
        "source_type": "official_state_tourism_event_page",
        "publication_date": "2026 (event calendar)",
        "accessed_date": ACCESS_DATE,
        "inspection_method": "Opened and read event, ritual and 2026 calendar text; no automated collection.",
        "linked_temple_ids": ["jagannath"],
        "categories_with_relevant_source_content": ["festivals_traditions", "religious_cultural_significance"],
    },
]

docs = read_json(DOCS_PATH)
catalogue = read_json(CATALOGUE_PATH)
plan = read_json(PLAN_PATH)
doc_ids = {item["document_id"] for item in docs}
if any(item["document_id"] in doc_ids for item in documents):
    raise SystemExit("Refusing to append: a checkpoint document ID already exists")
catalogue_by_id = {item["id"]: item for item in catalogue}
plan_by_id = {item["temple_id"]: item for item in plan["temples"]}
for document in documents:
    if document["temple_id"] not in catalogue_by_id or document["temple_id"] not in plan_by_id:
        raise SystemExit(f"Unknown temple reference: {document['temple_id']}")
    docs.append(document)
    catalogue_by_id[document["temple_id"]].setdefault("document_ids", []).append(document["document_id"])

for temple_id in ("meenakshi", "kashi_vishwanath", "jagannath"):
    item = plan_by_id[temple_id]
    item["research_status"] = "primary_source_inspected_partial_categories"
    item["research_notes"] = (item.get("research_notes", "") + " External pages inspected 2026-11-05; category gaps remain.").strip()
    item["remaining_gaps"] = sorted({category for category, state in item.get("categories", {}).items() if state.get("coverage_status") in {"Missing", "Basic"}})
    item["error_or_access_limitations"] = []

all_source_checks = plan.get("source_checks_this_operation", [])
known_urls = {s["source_url"] for s in all_source_checks}
all_source_checks.extend(s for s in source_checks if s["source_url"] not in known_urls)
plan["source_checks_this_operation"] = all_source_checks
plan.setdefault("inaccessible_or_unmapped_source_attempts", []).append({
    "source_url": "https://puri.odisha.gov.in/en/tourism/tourist-places/shree-jagannath-temple",
    "linked_temple_ids": ["jagannath"],
    "attempted_date": ACCESS_DATE,
    "status": "timeout; no page content used",
})
plan["inaccessible_or_unmapped_source_attempts"].append({
    "source_url": "https://www.shrikashivishwanath.org/mythology",
    "linked_temple_ids": ["kashi_vishwanath"],
    "attempted_date": ACCESS_DATE,
    "status": "403 Forbidden; search snippet not used as source evidence",
})
all_docs_by_temple: dict[str, list[str]] = {}
for doc in docs:
    if doc["document_id"].startswith(("all217_research_20261105_", "resume_research_20261105_")):
        all_docs_by_temple.setdefault(doc["temple_id"], []).append(doc["document_id"])
for item in plan["temples"]:
    temple_id = item["temple_id"]
    linked_sources = [s for s in all_source_checks if temple_id in s.get("linked_temple_ids", [])]
    item["sources_inspected"] = sorted({s["source_url"] for s in linked_sources})
    item["categories_researched"] = sorted({category for s in linked_sources for category in s.get("categories_with_relevant_source_content", [])})
    item["documents_added"] = sorted(set(all_docs_by_temple.get(temple_id, [])))
    item["documents_added_this_operation"] = item["documents_added"]
    item.setdefault("remaining_gaps", item.get("missing_information", []))
    item.setdefault("error_or_access_limitations", [])
if "jagannath" in plan_by_id:
    plan_by_id["jagannath"]["error_or_access_limitations"].append("Puri district administration temple page timed out; Odisha Tourism pages were used instead.")
if "kashi_vishwanath" in plan_by_id:
    plan_by_id["kashi_vishwanath"]["error_or_access_limitations"].append("Temple mythology page returned 403; no claims from its search snippet were used.")
plan["temples_with_external_source_pages_inspected_this_operation"] = sum(bool(t["sources_inspected"]) for t in plan["temples"])
plan["temples_not_yet_researched_this_operation"] = sum(not t["sources_inspected"] for t in plan["temples"])
plan["current_knowledge_document_count"] = len(docs)
plan["new_documents_added_this_operation"] = sum(len(t["documents_added_this_operation"]) for t in plan["temples"])
plan["temples_with_new_documents_pending_review"] = sum(bool(t["documents_added_this_operation"]) for t in plan["temples"])
plan["last_updated_utc"] = datetime.now(timezone.utc).isoformat()
plan["research_status_note"] = "Resumed source research from the saved checkpoint. Only temples with opened source pages are marked inspected; every category gap remains open until evidence has been checked."

write_json(DOCS_PATH, docs)
write_json(CATALOGUE_PATH, catalogue)
write_json(PLAN_PATH, plan)
print(json.dumps({"documents": len(docs), "new_documents": len(documents), "catalogue": len(catalogue),
                  "inspected_temple_records": plan["temples_with_external_source_pages_inspected_this_operation"],
                  "not_yet_inspected": plan["temples_not_yet_researched_this_operation"],
                  "new_document_ids": [d["document_id"] for d in documents]}, ensure_ascii=False, indent=2))
