"""Record inspected Himachal Tourism material for named Chamba temples."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TODAY = "2026-11-05"
URL = "https://himachaltourism.gov.in/destination/temples/"


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
        "manimahesh": "asi_himachal_pra_7509a21fdaa8af22",
        "lakshmana": "asi_himachal_pra_3e34b97076b4e1a3",
        "ganesh": "asi_himachal_pra_c5706cddb70077f6",
        "narsingh": "asi_himachal_pra_4a3a5f31aa66c811",
        "lakshmi_narayan": "asi_himachal_pra_a6a66c91268cdcdf",
        "hari_rai": "asi_himachal_pra_56b348db7df5aa99",
    }
    source = {
        "title": "Temples",
        "publisher": "Himachal Tourism, Government of Himachal Pradesh",
        "source_type": "official_state_tourism_page",
        "publication_date": None,
    }

    def add(tid: str, suffix: str, title: str, topic: str, body: str) -> None:
        did = f"systematic_research_20261105_{suffix}"
        if did in existing:
            return
        temple = by_id[tid]
        text = body + " Accessed 2026-11-05."
        docs.append({
            "document_id": did,
            "temple_id": tid,
            "temple_name": temple.get("canonical_name") or temple.get("names", [tid])[0],
            "state": temple.get("state"),
            "district": temple.get("district"),
            "topic": topic,
            "title": title,
            "source_title": source["title"],
            "source_url": URL,
            "publisher": source["publisher"],
            "source_type": source["source_type"],
            "language": "en",
            "publication_date": source["publication_date"],
            "retrieval_date": TODAY,
            "collection_timestamp": datetime.now(timezone.utc).isoformat(),
            "content_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "verification_status": "source_review_pending",
            "review_status": "pending_human_review",
            "is_paraphrase": True,
            "text": text,
        })
        existing.add(did)
        refs = temple.setdefault("document_ids", [])
        if did not in refs:
            refs.append(did)

    add(ids["manimahesh"], "bharmour_manimahesh_chaurasi_tourism_history_religion", "Chaurasi complex and Mani Mahesh shrine: Himachal Tourism account", "history_architecture_religion_culture", "Himachal Tourism describes Chaurasi as a complex of 84 temples and shrines in Bharmaur, dating it to the 7th century. It identifies the main temple as Mani Mahesh, dedicated to Shiva, and names Lakshana Devi as another important shrine. The page describes an ornate structural pediment at the complex entrance, says surrounding shrines include symbolic Shiva lingas, and reports a belief that the Manimahesh Lake pilgrimage is incomplete without a visit to Chaurasi. These are the tourism department's statements and reported belief; the source does not provide a temple-specific inscriptional citation or detailed construction chronology. The separate lake yatra details are not conflated with this Bharmour shrine.")
    add(ids["lakshmi_narayan"], "chamba_lakshmi_narayan_tourism_architecture_patronage", "Lakshmi Narayan complex, Chamba: architecture and reported patronage", "history_architecture_religion", "Himachal Tourism describes the Chamba Lakshmi Narayan complex as six stone temples in shikhara style, with circular slate-roofed chhatries supported on wooden beams. It identifies the main temple as dedicated to Vishnu and attributes its construction in the 10th century to Raja Sahil Varman, in connection with the founding of Chamba. The page describes chiselled stone walls, small arches on carved pillars and sculpted deities, and reports that three temples are dedicated to Shiva and one to Radha-Krishna. A separate Government of Himachal Pradesh pilgrimage page gives a broad 8th-century date for the group and calls Lakshmi Narayan its oldest shrine. These accounts differ in chronology and should be reviewed rather than silently reconciled; neither page supplies the inscriptional evidence in the passages inspected.")
    add(ids["hari_rai"], "chamba_hari_rai_tourism_architecture_cultural_context", "Hari Rai Temple, Chamba: official tourism description", "history_architecture_religion_cultural_significance", "Himachal Tourism describes Hari Rai as an 11th-century shikhara-style Vishnu temple on a stone platform at the north-west corner of Chamba's Chaugan. The page identifies the image as Vishnu in the Chaturmurti form and describes the Chaugan as a historic civic space and former principal entry area of Chamba. It says the temple is approached by stepping stones. The inspected account does not name a builder, cite an inscription, describe annual festivals or give current opening arrangements; those details remain open research questions.")

    checks = plan.setdefault("source_checks_this_operation", [])
    checks.append({
        "source_title": source["title"], "source_url": URL,
        "publisher": source["publisher"], "source_type": source["source_type"],
        "publication_date": None, "accessed_date": TODAY,
        "linked_temple_ids": [ids["manimahesh"], ids["lakshmana"], ids["lakshmi_narayan"], ids["hari_rai"]],
        "categories_with_relevant_source_content": ["historical_background", "architecture", "religious_cultural_significance"],
        "inspection_method": "The official tourism HTML page returned HTTP 200; its named Chaurasi, Lakshmi Narayan and Hari Rai sections were read from the page body.",
        "note": "The page is an official tourism source, not an archaeological report. It is used for the named claims only; Chamba Lakshmi Narayan chronology differs from the state's separate broad 8th-century account and is flagged for review. Other briefly named shrines receive no unsupported detail.",
    })
    unique = {}
    for item in checks:
        unique[(item.get("source_url"), tuple(sorted(item.get("linked_temple_ids", []))))] = item
    plan["source_checks_this_operation"] = list(unique.values())
    added_ids = [
        "systematic_research_20261105_bharmour_manimahesh_chaurasi_tourism_history_religion",
        "systematic_research_20261105_chamba_lakshmi_narayan_tourism_architecture_patronage",
        "systematic_research_20261105_chamba_hari_rai_tourism_architecture_cultural_context",
    ]
    plan["last_checkpoint"] = {
        "checkpoint_id": "systematic_research_20261105_himachal_group_05",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "temple_ids": list(ids.values()),
        "documents_added": [did for did in added_ids if did in existing],
        "note": "Opened and read the official Himachal Tourism page; all claims remain pending source review. Conflicting chronology is explicitly retained for human review.",
    }
    catalogue_path.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    doc_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"catalogue": len(catalogue), "documents": len(docs), "added": plan["last_checkpoint"]["documents_added"]}, indent=2))


if __name__ == "__main__":
    main()
