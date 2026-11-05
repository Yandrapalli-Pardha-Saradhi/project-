"""Record actual inspected Himachal government/tourism source material."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TODAY = "2026-11-05"


def main() -> None:
    catalogue_path = DATA / "catalogue.json"
    doc_path = DATA / "raw" / "temple_sources.json"
    plan_path = DATA / "research_plan_all_217.json"
    catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
    docs = json.loads(doc_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    by_id = {t["id"]: t for t in catalogue}
    existing = {d.get("document_id") for d in docs}
    ids = {
        "ganesh": "asi_himachal_pra_c5706cddb70077f6",
        "lakshana": "asi_himachal_pra_3e34b97076b4e1a3",
        "manimahesh": "asi_himachal_pra_7509a21fdaa8af22",
        "narsingh": "asi_himachal_pra_4a3a5f31aa66c811",
        "lakshmi_narayan": "asi_himachal_pra_a6a66c91268cdcdf",
    }
    sources = {
        "apursa": {
            "title": "Adopt a Heritage / Apni Dharohar Apni Pehchaan and Aaj Purani Rahon Se: Himachal Pradesh",
            "url": "https://lac.hp.gov.in/wp-content/themes/capital/pdf/APURSA-converted.pdf",
            "publisher": "Ministry of Tourism, Government of India; Himachal Pradesh project material",
            "type": "government_heritage_project_pdf",
            "date": "2019-01",
        },
        "pilgrimages": {
            "title": "Hindu Pilgrimage",
            "url": "https://himachal.nic.in/Content/HtmlPage?qs=LdEF+AuYkB4Dve235DK9HQ%3D%3D",
            "publisher": "Government of Himachal Pradesh",
            "type": "official_state_government_page",
            "date": None,
        },
        "chamba_yatra": {
            "title": "Manimahesh Yatra",
            "url": "https://hpchamba.nic.in/manimahesh-yatra/",
            "publisher": "District Chamba, Government of Himachal Pradesh",
            "type": "official_district_administration_page",
            "date": None,
        },
        "temple_trust": {
            "title": "Temples Trust: List of Acquired Temples",
            "url": "https://lac.hp.gov.in/temples-trust/",
            "publisher": "Language, Art and Culture Department, Government of Himachal Pradesh",
            "type": "official_state_department_page",
            "date": None,
        },
    }

    def add(tid: str, suffix: str, title: str, topic: str, body: str, source: dict, pages: str | None = None) -> None:
        doc_id = f"systematic_research_20261105_{suffix}"
        if doc_id in existing:
            return
        temple = by_id[tid]
        text = body + " Accessed 2026-11-05." + (f" PDF reference: {pages}." if pages else "")
        docs.append({
            "document_id": doc_id,
            "temple_id": tid,
            "temple_name": temple.get("canonical_name") or temple.get("names", [tid])[0],
            "state": temple.get("state"),
            "district": temple.get("district"),
            "topic": topic,
            "title": title,
            "source_title": source["title"],
            "source_url": source["url"],
            "publisher": source["publisher"],
            "source_type": source["type"],
            "language": "en",
            "publication_date": source["date"],
            "retrieval_date": TODAY,
            "collection_timestamp": datetime.now(timezone.utc).isoformat(),
            "content_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "verification_status": "source_review_pending",
            "review_status": "pending_human_review",
            "is_paraphrase": True,
            "text": text,
        })
        existing.add(doc_id)
        refs = temple.setdefault("document_ids", [])
        if doc_id not in refs:
            refs.append(doc_id)

    group_text = (
        "A 2019 Government of India tourism-project profile describes the Chaurasi temple complex at Bharmour as a group of 84 shrines and names this temple among four shrines under ASI Shimla Circle jurisdiction. "
        "The profile attributes patronage of the four named shrines to Meru Varmana, described there as an early Varman ruler of Bharmour (then called Bramhapur), and connects the shrines with the cultural history of Chamba and the Manimahesh pilgrimage. "
        "These are statements in the project profile; the inspected material does not provide a temple-specific inscriptional citation, an independently corroborated construction date, or detailed individual architectural descriptions."
    )
    add(ids["ganesh"], "bharmour_ganesh_chaurasi_asi_heritage_context", "Ganesh Temple, Bharmour: Chaurasi complex and documented heritage context", "heritage_conservation_history_religion", group_text, sources["apursa"], "printed/project page 13 (PDF page 12), Chaurasi Temple Complex profile")
    add(ids["lakshana"], "bharmour_lakshana_devi_chaurasi_asi_heritage_context", "Lakshana Devi Temple, Bharmour: Chaurasi complex and documented heritage context", "heritage_conservation_history_religion", group_text, sources["apursa"], "printed/project page 13 (PDF page 12), Chaurasi Temple Complex profile")
    add(ids["manimahesh"], "bharmour_manimahesh_chaurasi_asi_heritage_context", "Mani Mahesh Temple, Bharmour: Chaurasi complex and pilgrimage context", "heritage_conservation_history_religion", group_text + " The district administration's Manimahesh Yatra page concerns the lake pilgrimage route and fair; its lake-based ritual details are not attributed here to the separate Bharmour temple.", sources["apursa"], "printed/project page 13 (PDF page 12), Chaurasi Temple Complex profile")
    add(ids["narsingh"], "bharmour_narsingh_chaurasi_asi_heritage_context", "Narsingh Temple, Bharmour: Chaurasi complex and documented heritage context", "heritage_conservation_history_religion", group_text, sources["apursa"], "printed/project page 13 (PDF page 12), Chaurasi Temple Complex profile")
    add(ids["lakshmi_narayan"], "chamba_lakshmi_narayan_group_state_history_architecture", "Lakshmi Narayan group, Chamba: state account of history and architecture", "history_architecture_religion", "The Government of Himachal Pradesh describes the Lakshmi Narayan complex in Chamba town as six finely carved stone temples dedicated to Shiva and Vishnu, with tall shikharas. Its pilgrimage page dates the group broadly to the 8th century CE and identifies Lakshmi Narayan as the oldest temple in the group. The source does not detail inscriptions, individual construction phases, festivals, current timings, or entry conditions; the broad date and description are retained as the state's account pending review.", sources["pilgrimages"])

    checks = plan.setdefault("source_checks_this_operation", [])
    checks.extend([
        {"source_title": sources["apursa"]["title"], "source_url": sources["apursa"]["url"], "publisher": sources["apursa"]["publisher"], "source_type": sources["apursa"]["type"], "publication_date": sources["apursa"]["date"], "accessed_date": TODAY, "linked_temple_ids": [ids[k] for k in ("ganesh", "lakshana", "manimahesh", "narsingh")], "categories_with_relevant_source_content": ["history", "heritage_conservation", "religious_cultural_significance", "visitor_information"], "inspection_method": "Opened government PDF and inspected the Chaurasi profile, temple list and project details; page associations were matched to the four named catalogue entries.", "note": "The document is a 2019 project profile, not a detailed archaeological monograph. Patronage attribution and heritage status remain pending human review."},
        {"source_title": sources["pilgrimages"]["title"], "source_url": sources["pilgrimages"]["url"], "publisher": sources["pilgrimages"]["publisher"], "source_type": sources["pilgrimages"]["type"], "publication_date": None, "accessed_date": TODAY, "linked_temple_ids": [ids["lakshmi_narayan"]], "categories_with_relevant_source_content": ["history", "architecture", "religious_cultural_significance"], "inspection_method": "Opened the state government page and read the Lakshmi Narayan section.", "note": "Supports a broad state account of group size, dedication, shikhara description, relative age and approximate date; no visitor currentness claim."},
        {"source_title": sources["chamba_yatra"]["title"], "source_url": sources["chamba_yatra"]["url"], "publisher": sources["chamba_yatra"]["publisher"], "source_type": sources["chamba_yatra"]["type"], "publication_date": None, "accessed_date": TODAY, "linked_temple_ids": [ids["manimahesh"]], "categories_with_relevant_source_content": ["religious_cultural_significance", "festivals_traditions", "visitor_information"], "inspection_method": "Opened the district page and read the yatra, pilgrimage, route and 2026 advisory sections.", "note": "Page covers Manimahesh Lake and yatra. It is not used as evidence for architecture or facts about the distinct Bharmour Mani Mahesh Temple."},
        {"source_title": sources["temple_trust"]["title"], "source_url": sources["temple_trust"]["url"], "publisher": sources["temple_trust"]["publisher"], "source_type": sources["temple_trust"]["type"], "publication_date": None, "accessed_date": TODAY, "linked_temple_ids": [ids["lakshmi_narayan"], ids["manimahesh"]], "categories_with_relevant_source_content": ["heritage_conservation"], "inspection_method": "Opened the state department page and inspected its acquired-temples table.", "note": "Shows state temple-management takeover dates, which are administrative facts and not conservation or ASI-protection status."},
    ])
    # Preserve distinct source/temple relationships without duplicate rows.
    unique = {}
    for item in checks:
        key = (item.get("source_url"), tuple(sorted(item.get("linked_temple_ids", []))))
        unique[key] = item
    plan["source_checks_this_operation"] = list(unique.values())
    added_ids = [
        "systematic_research_20261105_bharmour_ganesh_chaurasi_asi_heritage_context",
        "systematic_research_20261105_bharmour_lakshana_devi_chaurasi_asi_heritage_context",
        "systematic_research_20261105_bharmour_manimahesh_chaurasi_asi_heritage_context",
        "systematic_research_20261105_bharmour_narsingh_chaurasi_asi_heritage_context",
        "systematic_research_20261105_chamba_lakshmi_narayan_group_state_history_architecture",
    ]
    plan["last_checkpoint"] = {
        "checkpoint_id": "systematic_research_20261105_himachal_group_04",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "temple_ids": list(ids.values()),
        "documents_added": [x for x in added_ids if x in existing],
        "note": "Official Himachal Pradesh and Government of India pages/PDF were opened and inspected. New material remains pending human review; no source permissions or collection gates changed.",
    }
    catalogue_path.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    doc_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"catalogue": len(catalogue), "documents": len(docs), "added": plan["last_checkpoint"]["documents_added"], "temples": list(ids.values())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
