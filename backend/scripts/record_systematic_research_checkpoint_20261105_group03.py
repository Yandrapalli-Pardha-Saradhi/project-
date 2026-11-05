"""Record manually inspected Assam Tourism source pages for four temples."""
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
    by_id = {x["id"]: x for x in catalogue}
    doc_path = DATA / "raw" / "temple_sources.json"
    docs = json.loads(doc_path.read_text(encoding="utf-8"))
    ids = {x.get("document_id") for x in docs}
    plan_path = DATA / "research_plan_all_217.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    sources = {
        "hayagriva": {"title": "Hayagriva Madhava Temple", "url": "https://assamtourism.gov.in/Hayagriva-Madhava-Temple.php", "publisher": "Assam Tourism Development Corporation", "type": "official_state_tourism_page", "date": None},
        "coffee": {"title": "Assam Tourism Coffee Table Book", "url": "https://publications.assamtourism.gov.in/publications/files/Assam_Tourism_Coffee_Table_Book.pdf", "publisher": "Assam Tourism Development Corporation", "type": "official_state_tourism_publication_pdf", "date": "2018"},
    }

    def add(tid: str, suffix: str, title: str, topic: str, text: str, src: dict, pages: str | None = None) -> None:
        did = "systematic_research_20261105_" + suffix
        if did in ids:
            return
        temple = by_id[tid]
        provenance = f" Accessed 2026-11-05." + (f" PDF reference: {pages}." if pages else "")
        full_text = text + provenance
        doc = {
            "document_id": did, "temple_id": tid,
            "temple_name": temple.get("canonical_name") or temple.get("names", [tid])[0],
            "state": temple.get("state"), "district": temple.get("district"),
            "topic": topic, "title": title,
            "source_title": src["title"], "source_url": src["url"], "publisher": src["publisher"],
            "source_type": src["type"], "language": "en", "publication_date": src["date"],
            "retrieval_date": TODAY, "collection_timestamp": datetime.now(timezone.utc).isoformat(),
            "content_hash": hashlib.sha256(full_text.encode("utf-8")).hexdigest(),
            "verification_status": "source_review_pending", "review_status": "pending_human_review",
            "is_paraphrase": True, "text": full_text,
        }
        docs.append(doc); ids.add(did)
        linked = temple.setdefault("document_ids", [])
        if did not in linked: linked.append(did)

    add("asi_assam_0aecea616e14afa3", "hajo_hayagriva_assam_tourism_history_culture_festivals",
        "Hayagriva Madhava Temple at Hajo: state tourism account of history, cultural significance and festivals",
        "history_architecture_religion_festivals",
        "Assam Tourism places the Hayagriva Madhava Temple on Monikut Hill, 28 kilometres west of Guwahati, and describes its architecture as combining Hindu and Buddhist styles. The tourism page attributes construction to King Raghu Deva Narayan in 1583. It describes the temple as a place associated with interreligious pilgrimage and says Doul Utsav is celebrated at the adjacent Doul Griha; it also names Bihu and Janmashtami as annual observances at the temple. The source does not give an inscriptional basis for its construction attribution, a detailed architectural inventory, current timings or fees. The date and festival claims are the state tourism page's account and remain pending review.", sources["hayagriva"])
    add("asi_assam_0aecea616e14afa3", "hajo_hayagriva_assam_tourism_interfaith_context",
        "Hayagriva Madhava and shared Hindu-Buddhist reverence in Hajo",
        "religious_cultural_significance",
        "Assam Tourism's 2018 coffee-table book describes Hayagriva-Madhava as a Vishnu shrine on Manikut Hill in Hajo and records a Buddhist tradition that identifies the temple image with Gautama Buddha. The account says Buddhist visitors, particularly from Bhutan, visit the shrine. This is reported as a religious interpretation and pilgrimage tradition, not as a historical identification established by archaeological evidence. The book situates the temple within Hajo's wider multi-faith landscape; that regional context is not used here to infer temple-specific rituals beyond what the source states.", sources["coffee"], "printed page 72")
    add("asi_assam_dbf0ecb97451eb87", "negheriting_sivadol_assam_tourism_history_architecture",
        "Negheriting Shiva Doul: state tourism history, reconstruction and surrounding shrines",
        "history_architecture_religion_visitor_information",
        "The Assam Tourism 2018 coffee-table book identifies Negheriting Shiva-dol as a stone temple in the Dergaon area and dates it broadly to the 9th century. The passage situates it in the wider Golaghat/Kaziranga region. The inspected source does not establish its builder, exact construction chronology, surrounding subsidiary shrines, festivals, inscriptions, or current visitor arrangements. The broad date is the state tourism publication's statement and remains pending human review.", sources["coffee"], "printed page 72")
    add("asi_assam_53f3d143b7f21899", "sivasagar_sivadol_assam_tourism_context",
        "Siva Dole at Sibsagar: Assam Tourism account of its Ahom-period setting",
        "history_architecture_heritage",
        "Assam Tourism's 2018 coffee-table book places the Shiva-dol in Sivasagar's historic landscape of temples and large water tanks. It describes Sivasagar as the former Ahom capital, refers to the Shiva-dol and adjacent Sivasagar Tank, and mentions Joy-dol, Vishnu-dol and Devi-dol among the area's other temples. The inspected passages do not establish an exact construction year, named royal patron, temple-specific inscription, or detailed architectural features. The district-wide context is not treated as evidence for the catalogued Gaurisagar or Joysagar temples.", sources["coffee"], "printed pages 66 and 72")
    add("asi_assam_21748e5141ece6d2", "suryapahar_assam_tourism_archaeological_landscape",
        "Suryapahar: Assam Tourism description of the multi-religious archaeological landscape",
        "heritage_archaeology_religious_cultural_significance",
        "Assam Tourism's 2018 coffee-table book describes Suryapahar in Goalpara as a hillock archaeological site with Hindu, Buddhist and Jain remains. It reports numerous engraved Shiva lingas, Buddhist stupas and sculptures associated with Jain religious traditions, and interprets the material as evidence of a long-lived settlement. In a separate section it refers to granite Buddhist votive stupas and the coexistence of Hindu, Buddhist and Jain remains. The publication does not give a secure temple-by-temple chronology or identify the Dasabhaja Devasthan structure specifically in the inspected passage; those details remain research gaps.", sources["coffee"], "printed pages 66 and 72")

    (DATA / "catalogue.json").write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    doc_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    checks = plan.setdefault("source_checks_this_operation", [])
    checks.extend([
        {"source_title": sources["hayagriva"]["title"], "source_url": sources["hayagriva"]["url"], "publisher": sources["hayagriva"]["publisher"], "source_type": sources["hayagriva"]["type"], "publication_date": None, "accessed_date": TODAY, "linked_temple_ids": ["asi_assam_0aecea616e14afa3"], "categories_with_relevant_source_content": ["historical_background", "architecture", "religious_cultural_significance", "festivals_traditions"], "inspection_method": "Opened and read the named Assam Tourism page; temple identity and locality matched.", "note": "Supports state tourism account of construction attribution, architectural style, location and named observances; not inscriptional corroboration."},
        {"source_title": sources["coffee"]["title"], "source_url": sources["coffee"]["url"], "publisher": sources["coffee"]["publisher"], "source_type": sources["coffee"]["type"], "publication_date": "2018", "accessed_date": TODAY, "linked_temple_ids": ["asi_assam_0aecea616e14afa3", "asi_assam_dbf0ecb97451eb87", "asi_assam_53f3d143b7f21899", "asi_assam_21748e5141ece6d2"], "categories_with_relevant_source_content": ["historical_background", "architecture", "religious_cultural_significance", "heritage_conservation"], "inspection_method": "Opened and inspected the state tourism PDF; read the temple and Suryapahar passages with printed page references.", "note": "Each temple relationship is explicit in the inspected text; broad regional passages are not used to infer unsupported temple facts."},
    ])
    unique = {}
    for src in checks: unique[(src.get("source_url"), tuple(sorted(src.get("linked_temple_ids", []))))] = src
    plan["source_checks_this_operation"] = list(unique.values())
    plan["last_checkpoint"] = {
        "checkpoint_id": "systematic_research_20261105_assam_group_03",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "temple_ids": ["asi_assam_0aecea616e14afa3", "asi_assam_dbf0ecb97451eb87", "asi_assam_53f3d143b7f21899", "asi_assam_21748e5141ece6d2"],
        "documents_added": ["systematic_research_20261105_hajo_hayagriva_assam_tourism_history_culture_festivals", "systematic_research_20261105_hajo_hayagriva_assam_tourism_interfaith_context", "systematic_research_20261105_negheriting_sivadol_assam_tourism_history_architecture", "systematic_research_20261105_sivasagar_sivadol_assam_tourism_context", "systematic_research_20261105_suryapahar_assam_tourism_archaeological_landscape"],
        "note": "Manually inspected official Assam Tourism page and publication PDF. Claims remain pending human review; no bulk crawling or permissions changes.",
    }
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"knowledge_documents": len(docs), "added": plan["last_checkpoint"]["documents_added"], "temples": plan["last_checkpoint"]["temple_ids"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
