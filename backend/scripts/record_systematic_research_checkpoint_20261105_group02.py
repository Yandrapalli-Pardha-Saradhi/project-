"""Record ASI conservation-report evidence from manually inspected PDFs."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TODAY = "2026-11-05"


def main() -> None:
    catalogue = json.loads((DATA / "catalogue.json").read_text(encoding="utf-8"))
    by_id = {row["id"]: row for row in catalogue}
    docs_path = DATA / "raw" / "temple_sources.json"
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    doc_ids = {doc.get("document_id") for doc in docs}
    plan_path = DATA / "research_plan_all_217.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    src1956 = {
        "title": "Indian Archaeology 1956-57: A Review",
        "url": "https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%201956-57%20A%20Review.pdf",
        "publisher": "Department of Archaeology, Government of India / Archaeological Survey of India",
        "type": "asi_annual_conservation_review_pdf", "date": "1957",
    }
    src2012 = {
        "title": "Indian Archaeology 2012-13: A Review",
        "url": "https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%20%202012%20-%202013%20%20A%20Review.pdf",
        "publisher": "Archaeological Survey of India, Government of India",
        "type": "asi_annual_conservation_review_pdf", "date": "2015",
    }
    src2007 = {
        "title": "Rajya Sabha Unstarred Question 162: Centrally protected monuments in Andhra Pradesh",
        "url": "https://rsdebate.nic.in/bitstream/123456789/35430/1/PQ_210_27022007_U162_p55_p61.pdf",
        "publisher": "Rajya Sabha Secretariat / Ministry of Culture, Government of India",
        "type": "official_parliamentary_answer_pdf", "date": "2007-02-27",
    }

    def add_doc(tid: str, suffix: str, title: str, text: str, src: dict, topic: str = "heritage_conservation", pages: str = "") -> None:
        did = f"systematic_research_20261105_{suffix}"
        if did in doc_ids:
            return
        temple = by_id[tid]
        doc = {
            "document_id": did, "temple_id": tid,
            "temple_name": temple.get("canonical_name") or temple.get("names", [tid])[0],
            "state": temple.get("state"), "district": temple.get("district"),
            "topic": topic, "title": title,
            "source_title": src["title"], "source_url": src["url"], "publisher": src["publisher"],
            "source_type": src["type"], "language": "en", "publication_date": src["date"],
            "retrieval_date": TODAY, "collection_timestamp": datetime.now(timezone.utc).isoformat(),
            "content_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "verification_status": "source_review_pending", "review_status": "pending_human_review",
            "is_paraphrase": True, "text": text + (f" Report reference: {pages}; accessed 2026-11-05." if pages else " Accessed 2026-11-05."),
        }
        # Hash the final stored content, including its provenance note.
        doc["content_hash"] = hashlib.sha256(doc["text"].encode("utf-8")).hexdigest()
        docs.append(doc)
        doc_ids.add(did)
        linked = temple.setdefault("document_ids", [])
        if did not in linked:
            linked.append(did)

    ap = "asi_andhra_prade_"
    add_doc(ap + "bead535e8e3f76eb", "lepakshi_veerabhadra_asi_conservation_1956", "Lepakshi Veerabhadra Temple: ASI conservation work recorded in 1956-57",
            "The Archaeological Survey of India's 1956-57 review records conservation work at the Virabhadra Temple, Lepakshi: central floor slabs were reset and open joints filled. This is a dated report of work undertaken in that review year, not a present-condition assessment or a full conservation history.", src1956, pages="printed page 51")
    add_doc(ap + "34fdc7ad2433488f", "lepakshi_basavannah_asi_conservation_1956", "Lepakshi Basavanna Temple: ASI platform work recorded in 1956-57",
            "The Archaeological Survey of India's 1956-57 review states that a cut-stone facing platform was constructed for the colossal bull at the Basavanna Temple, Lepakshi. This records one specific intervention in the review year; the source does not describe the temple's wider history, deity traditions, festivals, or current condition.", src1956, pages="printed page 51")
    add_doc(ap + "4824bbb04f702849", "gorantla_madhavaraya_asi_conservation_1956", "Madhavaraya Temple, Gorantla: ASI mandapa roof conservation in 1956-57",
            "The Archaeological Survey of India's 1956-57 review records that the terraces of the mandapas at Madhavaraya Temple, Gorantla, were made watertight. This is a historical conservation entry for 1956-57; it does not establish the present roof condition or the temple's full architectural chronology.", src1956, pages="printed page 51")
    add_doc(ap + "4824bbb04f702849", "gorantla_madhavaraya_asi_flooring_2012_13", "Madhavaraya Swamy Temple, Gorantla: ASI drainage and perimeter flooring works in 2012-13",
            "The Archaeological Survey of India's 2012-13 review reports granite flooring laid around the temple over a lime-concrete bed, following exposed original flooring members. It also records slopes and channels intended to drain rainwater away from the monument. This is a report of work documented for 2012-13, not a current condition survey.", src2012, pages="printed page 278")
    add_doc(ap + "5509b425f6edbf42", "kambaduru_mallikarjuna_asi_conservation_1956", "Mallikarjuna Temple, Kambaduru: ASI compound-wall conservation in 1956-57",
            "The Archaeological Survey of India's 1956-57 review records that broken portions of the compound wall at Mallikarjuna Temple, Kambaduru, were made watertight and stabilized; recessed pointing was applied to cut-stone masonry. These works are historical observations for the review year and should not be read as the monument's current condition.", src1956, pages="printed page 51")
    add_doc(ap + "e429b0544ae6aaa7", "mangapuram_venkateswara_asi_repairs_2012_13", "Venkateswara Vishnu Temple, Mangapuram: ASI repair entry from 2012-13",
            "The Archaeological Survey of India's 2012-13 review includes Venkateshwara Vishnu Temple, Mangapuram, in its preservation section and records repair work to damaged flooring in the temple's cloister mandapa at the south-east and north-east corners. The source does not specify the present condition or visitor arrangements.", src2012, pages="printed pages 278-279")
    add_doc(ap + "ba65914fa7b7de40", "sompalle_chennakesava_asi_landscape_2012_13", "Chenna Keshava Swamy Temple, Sompalem: ASI work recorded in 2012-13",
            "The Archaeological Survey of India's 2012-13 review records environmental beautification work around the monument, including a lawn bed within the protected area, under the printed name 'Sri Chenna Keshava Swamy Temple, Sompalem, District Chittor.' This is a dated site-management entry; it does not provide a temple history, festival calendar, or current visitor information. The catalogue locality is Sompalle; the spelling difference requires review.", src2012, pages="printed page 279")

    (DATA / "catalogue.json").write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    docs_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    checks = plan.setdefault("source_checks_this_operation", [])
    def record(src: dict, tids: list[str], notes: str, categories: list[str] | None = None) -> None:
        checks.append({"source_title": src["title"], "source_url": src["url"], "publisher": src["publisher"],
                       "source_type": src["type"], "publication_date": src["date"], "accessed_date": TODAY,
                       "linked_temple_ids": tids, "categories_with_relevant_source_content": categories or ["heritage_conservation"],
                       "inspection_method": "Opened the PDF and inspected the temple-specific entry and its page context.", "note": notes})
    record(src1956, [ap+"bead535e8e3f76eb", ap+"34fdc7ad2433488f", ap+"4824bbb04f702849", ap+"5509b425f6edbf42"],
           "Inspected named conservation entries in the official ASI review; work entries are dated historical evidence, not current-condition claims.")
    record(src2012, [ap+"4824bbb04f702849", ap+"e429b0544ae6aaa7", ap+"ba65914fa7b7de40"],
           "Inspected named preservation entries; Sompalem/Sompalle spelling equivalence is flagged for review.")
    record(src2007, [ap+"4824bbb04f702849", ap+"5509b425f6edbf42", ap+"bead535e8e3f76eb", ap+"34fdc7ad2433488f", ap+"994f268937105045", ap+"e74ff866d54d0cc2"],
           "Inspected the 2007 parliamentary list and matched temple/locality rows; it supports central-protection listing at that date only.")
    seen = {}
    for source in checks:
        seen[(source.get("source_url"), tuple(sorted(source.get("linked_temple_ids", []))))] = source
    plan["source_checks_this_operation"] = list(seen.values())
    plan["last_checkpoint"] = {
        "checkpoint_id": "systematic_research_20261105_ap_group_02",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "temple_ids": sorted({tid for s in plan["source_checks_this_operation"][-3:] for tid in s.get("linked_temple_ids", [])}),
        "documents_added": [d["document_id"] for d in docs if d.get("document_id", "").startswith("systematic_research_20261105_")],
        "note": "Manually inspected official ASI annual-review PDFs and parliamentary record; added only dated conservation evidence; pending human review.",
    }
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"knowledge_documents": len(docs), "systematic_documents": sum(d.get("document_id", "").startswith("systematic_research_20261105_") for d in docs),
                      "checkpoint_temple_ids": plan["last_checkpoint"]["temple_ids"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
