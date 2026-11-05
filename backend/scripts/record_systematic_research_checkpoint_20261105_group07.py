"""Record more Chamba/Kangra/Kullu facts from inspected Himachal sources."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TODAY = "2026-11-05"
TOURISM_URL = "https://himachaltourism.gov.in/destination/temples/"
APURSA_URL = "https://lac.hp.gov.in/wp-content/themes/capital/pdf/APURSA-converted.pdf"


def main() -> None:
    cp, dp, pp = DATA / "catalogue.json", DATA / "raw" / "temple_sources.json", DATA / "research_plan_all_217.json"
    catalogue, docs, plan = (json.loads(p.read_text(encoding="utf-8")) for p in (cp, dp, pp))
    temples = {t["id"]: t for t in catalogue}
    known = {d.get("document_id") for d in docs}
    source = {"title": "Temples", "publisher": "Himachal Tourism, Government of Himachal Pradesh", "type": "official_state_tourism_page", "date": None}
    today_text = " Accessed 2026-11-05."

    def add(tid: str, slug: str, title: str, topic: str, content: str, url: str = TOURISM_URL,
            source_title: str | None = None, publisher: str | None = None, source_type: str | None = None,
            pubdate: str | None = None, page: str | None = None) -> None:
        did = f"systematic_research_20261105_{slug}"
        if did in known:
            return
        temple = temples[tid]
        suffix = today_text + (f" PDF reference: {page}." if page else "")
        text = content + suffix
        docs.append({
            "document_id": did, "temple_id": tid,
            "temple_name": temple.get("canonical_name") or temple.get("names", [tid])[0],
            "state": temple.get("state"), "district": temple.get("district"),
            "topic": topic, "title": title,
            "source_title": source_title or source["title"], "source_url": url,
            "publisher": publisher or source["publisher"], "source_type": source_type or source["type"],
            "language": "en", "publication_date": pubdate, "retrieval_date": TODAY,
            "collection_timestamp": datetime.now(timezone.utc).isoformat(),
            "content_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "verification_status": "source_review_pending", "review_status": "pending_human_review",
            "is_paraphrase": True, "text": text,
        })
        known.add(did)
        refs = temple.setdefault("document_ids", [])
        if did not in refs:
            refs.append(did)

    add("asi_himachal_pra_a1ef8ff6339c407d", "masroor_rock_cut_tourism_architecture_history",
        "Masroor rock-cut temples: official tourism account and heritage features", "history_architecture_religion_heritage",
        "Himachal Tourism describes Masroor as an 8th-century monolithic rock-cut complex of 15 Indo-Aryan-style temples in Kangra. Its page names Shiva, Vishnu, Rama, Lakshmana, Sita and other Hindu deities, says the complex faces the eastern sun, and notes a rectangular courtyard pool that reflects the temple shikharas. A separate Government of India/Himachal heritage-project profile describes nineteen rock-cut temples and reports earthquake damage in 1905. The source accounts therefore differ on the complex's temple count; the discrepancy is retained for review. No UNESCO inscription is inferred from these sources.")
    add("asi_himachal_pra_2d93808a25e7f773", "bajaura_basheshar_tourism_architecture_religion",
        "Basheshar Mahadeo at Bajaura: official tourism account", "history_architecture_religion_heritage",
        "Himachal Tourism names the Vishveshvara Mahadev temple at Bajaura and says it is locally called Basheshara, matching the catalogue's Bajaura locality for Basheshar Mahadeo. The page describes a pyramidal, monolithic stone temple dedicated to Shiva, broadly dates it between the 9th and 12th centuries, and associates it with the Panch Dev Puja tradition. It notes large bas-reliefs and sculptural decoration and locates the temple near the Beas. The page does not provide an inscriptional basis for its date or name a patron; these claims remain pending review.")
    add("asi_himachal_pra_aac4a2248ad925db", "manali_hidimba_tourism_architecture_tradition",
        "Hidimba Devi Temple, Manali: state tourism account", "history_architecture_religion_cultural_significance",
        "Himachal Tourism describes the Hidimba temple as a four-tier stone pagoda with a wooden roof, built over a cave shrine and broadly dated to the 16th century. The page identifies Hidimba as the presiding deity and reports a local tradition that footprints of the goddess are preserved in the cave shrine. Its account also connects Hidimba with Bhima's wife in the Mahabharata; this is a religious narrative, not a claim of archaeological history. The inspected text does not give an inscriptional basis for the date or current visitor details.")
    add("asi_himachal_pra_d0cbd9e9b4b403a2", "baijnath_shivratri_festival_tourism_account",
        "Baijnath Temple: Shivratri worship and fair", "festivals_rituals_religious_cultural_significance",
        "Himachal Tourism says the Baijnath temple is decorated with flower garlands for Shivratri and that the town holds a Shivratri fair attracting devotees. The page presents this as a recurring local observance but does not give a current-year date, detailed ritual sequence, or administrative schedule. The temple's existing curated documents cover other aspects; this document adds only the festival account.")

    checks = plan.setdefault("source_checks_this_operation", [])
    checks.extend([
        {"source_title": "Temples", "source_url": TOURISM_URL, "publisher": "Himachal Tourism, Government of Himachal Pradesh", "source_type": "official_state_tourism_page", "publication_date": None, "accessed_date": TODAY, "linked_temple_ids": ["asi_himachal_pra_a1ef8ff6339c407d", "asi_himachal_pra_2d93808a25e7f773", "asi_himachal_pra_aac4a2248ad925db", "asi_himachal_pra_d0cbd9e9b4b403a2"], "categories_with_relevant_source_content": ["historical_background", "architecture", "religious_cultural_significance", "festivals_traditions", "visitor_information"], "inspection_method": "Fetched the official HTML page (HTTP 200), extracted and read its temple-specific paragraph sections; direct page content was inspected, not a search snippet.", "note": "Masroor source count conflicts with the 2019 Government of India/Himachal project PDF (15 versus 19); Baijnath festival statements are not current date/timing guidance."},
        {"source_title": "Adopt a Heritage / Apni Dharohar Apni Pehchaan and Aaj Purani Rahon Se: Himachal Pradesh", "source_url": APURSA_URL, "publisher": "Ministry of Tourism, Government of India; Himachal Pradesh project material", "source_type": "government_heritage_project_pdf", "publication_date": "2019-01", "accessed_date": TODAY, "linked_temple_ids": ["asi_himachal_pra_a1ef8ff6339c407d"], "categories_with_relevant_source_content": ["architecture", "heritage_conservation"], "inspection_method": "Opened and read the Masroor project profile (PDF lines/pages 349-371 in the extracted version).", "note": "Used only for the explicit Masroor temple count and reported 1905 earthquake damage; project profile is not an archaeological survey."},
    ])
    uniq = {}
    for c in checks:
        uniq[(c.get("source_url"), tuple(sorted(c.get("linked_temple_ids", []))))] = c
    plan["source_checks_this_operation"] = list(uniq.values())
    new_ids = [
        "systematic_research_20261105_masroor_rock_cut_tourism_architecture_history",
        "systematic_research_20261105_bajaura_basheshar_tourism_architecture_religion",
        "systematic_research_20261105_manali_hidimba_tourism_architecture_tradition",
        "systematic_research_20261105_baijnath_shivratri_festival_tourism_account",
    ]
    plan["last_checkpoint"] = {"checkpoint_id": "systematic_research_20261105_himachal_group_07", "completed_at_utc": datetime.now(timezone.utc).isoformat(), "temple_ids": ["asi_himachal_pra_a1ef8ff6339c407d", "asi_himachal_pra_2d93808a25e7f773", "asi_himachal_pra_aac4a2248ad925db", "asi_himachal_pra_d0cbd9e9b4b403a2"], "documents_added": [x for x in new_ids if x in known], "note": "Official tourism page and Government of India/Himachal heritage project profile were opened and read; claims remain pending human review."}
    cp.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    dp.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pp.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"catalogue": len(catalogue), "documents": len(docs), "added": plan["last_checkpoint"]["documents_added"]}, indent=2))


if __name__ == "__main__":
    main()
