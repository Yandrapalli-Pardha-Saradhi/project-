"""Record temple-specific claims from inspected Assam government/ASI sources."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
CHECKED = "2026-11-05"

# All URLs below were opened and the relevant sections inspected on 2026-11-05.
ITEMS = [
    {
        "temple_id": "asi_assam_68e3d36ac845c504",
        "document_id": "systematic_research_20261105_parbatiya_doorway_architecture",
        "title": "Parbatia temple remains: carved doorway and reported Gupta-style features",
        "topic": "architecture",
        "url": "https://directortourism.assam.gov.in/portlet-sub-innerpage/historical-monuments",
        "source_title": "Historical Monuments",
        "publisher": "Directorate of Tourism, Government of Assam",
        "source_type": "official_state_tourism_page",
        "publication_date": None,
        "page_ref": "HTML lines 67–69",
        "categories": ["architecture", "religious_cultural_significance"],
        "text": "The Assam Directorate of Tourism describes the surviving feature at Da-Parbatia near Tezpur as the ruins of a temple doorway. It identifies the doorway's style as characteristic of the early Gupta school. The door jambs are described as bearing figures of the river goddesses Ganga and Yamuna, each holding a garland, among decorative foliage. This is a description of the surviving sculptural doorway; the page does not provide a complete plan of the lost temple, name its presiding deity, or document a present ritual or festival. Accessed 5 November 2026.",
    },
    {
        "temple_id": "asi_assam_68e3d36ac845c504",
        "document_id": "systematic_research_20261105_parbatiya_history_state_tourism",
        "title": "Da-Parbatia near Tezpur: state tourism account of the temple remains",
        "topic": "historical_background_architecture",
        "url": "https://publications.assamtourism.gov.in/publications/files/Assam_Tourism_Coffee_Table_Book.pdf",
        "source_title": "Assam Tourism Coffee Table Book",
        "publisher": "Directorate of Tourism, Government of Assam",
        "source_type": "official_state_tourism_publication",
        "publication_date": "2018",
        "page_ref": "PDF text lines 484–485 (printed page to confirm in PDF)",
        "categories": ["historical_background", "architecture"],
        "text": "The 2018 Assam Tourism Coffee Table Book calls Dah Parbatia at Tezpur a fourth-century temple and characterizes it as an early example of sculptural art in Assam. It says the surviving remains include a rectangular stone doorway carved with Hindu deities. This date is reported as the publication's attribution; the separate district administration description inspected for this research confirms the carved doorway and its location but does not independently establish the fourth-century date. The evidence described here concerns the surviving doorway and does not establish the complete original temple form. Accessed 5 November 2026.",
    },
    {
        "temple_id": "asi_assam_68e3d36ac845c504",
        "document_id": "systematic_research_20261105_parbatiya_archival_preservation_record",
        "title": "Parbatia near Tezpur: archival record concerning preservation",
        "topic": "heritage_conservation",
        "url": "https://archives.assam.gov.in/sites/default/files/swf_utility_folder/departments/archives_webcomindia_org_oid_3/portlet/level_1/files/General%20%281920-1935%29_0.pdf",
        "source_title": "General (1920–1935): archival index",
        "publisher": "Assam State Archives, Government of Assam",
        "source_type": "official_state_archive_index",
        "publication_date": None,
        "page_ref": "PDF printed page 76; index lines 9100–9111; file reference X 7/25 (1925)",
        "categories": ["heritage_conservation", "historical_background"],
        "text": "The Assam State Archives index for the 1920–1935 General Department records lists a 1925 file, reference X 7/25, titled “Preservation of the mound and the stone temple at Parbatiya near Tezpur.” The index establishes that a government preservation file existed; the index entry alone does not reveal what work was proposed or completed, and it is not evidence of the monument's current condition or protection status. The underlying file would need to be consulted to establish those details. Accessed 5 November 2026.",
    },
    {
        "temple_id": "asi_assam_150626777a56d77d",
        "document_id": "systematic_research_20261105_gaurisagar_sivadol_asi_profile",
        "title": "Sivadol, Gaurisagar: Ahom patronage and temple architecture",
        "topic": "historical_background_architecture_religious_significance",
        "url": "https://www.asiguwahaticircle.gov.in/Sivadol%20Gaurisagar.html",
        "source_title": "31. Sivadol, Gaurisagar",
        "publisher": "Archaeological Survey of India, Guwahati Circle",
        "source_type": "official_asi_monument_profile",
        "publication_date": None,
        "page_ref": "HTML lines 60–67",
        "categories": ["historical_background", "architecture", "religious_cultural_significance"],
        "text": "The Archaeological Survey of India's Guwahati Circle profile says Sivadol at Gaurisagar was constructed by Phuleswari Devi, queen of Ahom king Siba Singha (CE 1714–1744), and dedicated to Shiva. It describes brick masonry, a garbhagriha and mukhamandapa, with the sanctum floor lower than the mandapa floor. The domical sikhara has vertical ridges and subsidiary angasikharas. ASI places the temple in the middle of a group of three temples on the northern bank of the Gaurisagar tank and notes an enclosing wall. The profile gives locality and approach information, but does not name festivals, provide visitor hours or establish a current visitor policy. Accessed 5 November 2026.",
    },
    {
        "temple_id": "asi_assam_150626777a56d77d",
        "document_id": "systematic_research_20261105_gaurisagar_sivadol_conservation_2000_01",
        "title": "Sivadol, Gaurisagar: conservation work reported for 2000–01",
        "topic": "heritage_conservation",
        "url": "https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%202000-2001%20A%20Review.pdf",
        "source_title": "Indian Archaeology 2000–01: A Review",
        "publisher": "Archaeological Survey of India / National Mission on Monuments and Antiquities",
        "source_type": "official_archaeological_conservation_report",
        "publication_date": "2001",
        "page_ref": "Printed page 253; section 205; PDF lines 5212–5213",
        "categories": ["heritage_conservation", "visitor_information"],
        "text": "The Archaeological Survey of India's 2000–01 annual review reports that decayed lime-concrete plaster on Sivadol's mandapa roof was replaced with matching plaster. It also records construction of a two-metre-wide brick-paved visitor path and restoration of the ancient compound walls on two sides using combination mortar. These are works reported for that specific reporting period; the report does not establish the temple's present condition or current visitor arrangements. Accessed 5 November 2026.",
    },
    {
        "temple_id": "asi_assam_3176178449463d6c",
        "document_id": "systematic_research_20261105_gaurisagar_vishnudol_asi_profile",
        "title": "Vishnudol, Gaurisagar: Ahom-period patronage and temple plan",
        "topic": "historical_background_architecture_religious_significance",
        "url": "https://www.asiguwahaticircle.gov.in/Bishnudol%20Gaurisagar.html",
        "source_title": "30. Vishnudol, Gaurisagar",
        "publisher": "Archaeological Survey of India, Guwahati Circle",
        "source_type": "official_asi_monument_profile",
        "publication_date": None,
        "page_ref": "HTML lines 60–69",
        "categories": ["historical_background", "architecture", "religious_cultural_significance"],
        "text": "The Archaeological Survey of India's Guwahati Circle identifies this monument as Vishnudol at Gaurisagar and says it was built by Siba Singha (CE 1714–1744) and dedicated to Vishnu. The catalogue record uses the names Bisdol (Bishnudol) (Gaurisagar); the ASI profile's Vishnudol spelling and Gaurisagar location are the basis for associating this evidence with that existing record. ASI describes brick masonry and a nilachala type domical sikhara with a honeycomb design. The plan comprises an octagonal garbhagriha, square mandapa and intervening antarala; the outer walls carry figures of divinities and the temple stands within an enclosure wall. The profile does not provide a festival calendar or current visitor details. Accessed 5 November 2026.",
    },
    {
        "temple_id": "asi_assam_3176178449463d6c",
        "document_id": "systematic_research_20261105_gaurisagar_vishnudol_conservation_2000_01",
        "title": "Vishnudol, Gaurisagar: compound-wall conservation reported for 2000–01",
        "topic": "heritage_conservation",
        "url": "https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%202000-2001%20A%20Review.pdf",
        "source_title": "Indian Archaeology 2000–01: A Review",
        "publisher": "Archaeological Survey of India / National Mission on Monuments and Antiquities",
        "source_type": "official_archaeological_conservation_report",
        "publication_date": "2001",
        "page_ref": "Printed page 253; section 206; PDF lines 5215–5216",
        "categories": ["heritage_conservation"],
        "text": "The Archaeological Survey of India's 2000–01 annual review states that conservation of the ancient compound wall around Vishnudol, Gaurisagar, was taken up. The brief entry does not specify the treatment or whether the work was completed, so it should not be read as a statement of present condition or conservation status. Accessed 5 November 2026.",
    },
]


def main() -> None:
    docs_path = DATA / "raw" / "temple_sources.json"
    catalogue_path = DATA / "catalogue.json"
    plan_path = DATA / "research_plan_all_217.json"
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    temples = {t["id"]: t for t in catalogue}
    queue = {t["temple_id"]: t for t in plan["temples"]}
    added: list[str] = []
    for spec in ITEMS:
        temple = temples[spec["temple_id"]]
        text = " ".join(spec["text"].split())
        doc = {
            "document_id": spec["document_id"], "temple_id": spec["temple_id"],
            "temple_name": temple["canonical_name"], "state": temple.get("state"),
            "district": temple.get("district"), "topic": spec["topic"],
            "title": spec["title"], "source_title": spec["source_title"],
            "source_url": spec["url"], "publisher": spec["publisher"],
            "source_type": spec["source_type"], "language": "en",
            "publication_date": spec["publication_date"], "retrieval_date": CHECKED,
            "collection_timestamp": datetime.now(timezone.utc).isoformat(),
            "source_page_reference": spec["page_ref"],
            "content_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "verification_status": "source_review_pending",
            "review_status": "pending_human_review", "is_paraphrase": True,
            "text": text,
        }
        existing = next((d for d in docs if d.get("document_id") == doc["document_id"]), None)
        if existing is None:
            docs.append(doc)
            added.append(doc["document_id"])
        elif existing.get("content_hash") != doc["content_hash"]:
            raise ValueError(f"Refusing to overwrite changed checkpoint document {doc['document_id']}")
        if doc["document_id"] not in temple.setdefault("document_ids", []):
            temple["document_ids"].append(doc["document_id"])
        row = queue[spec["temple_id"]]
        for key in ("sources_inspected", "previously_inspected_source_urls"):
            if spec["url"] not in row.setdefault(key, []):
                row[key].append(spec["url"])
        row["research_status"] = "enriched"
        row["enrichment_status"] = "enriched"
        row["last_completed_checkpoint"] = "2026-11-05-group16"
        row["documents_added_this_operation"] = sorted(set(row.get("documents_added_this_operation", [])) | {doc["document_id"]})
        row["page_evidence_categories"] = sorted(set(row.get("page_evidence_categories", [])) | set(spec["categories"]))
        note = f"Inspected {spec['source_title']} ({spec['url']}); relevant evidence at {spec['page_ref']}. Claims are limited to the source text; new document remains pending human review."
        row.setdefault("research_notes", [])
        if note not in row["research_notes"]:
            row["research_notes"].append(note)
    checks = plan.setdefault("source_checks_this_operation", [])
    check_by_url = {c.get("source_url"): c for c in checks}
    for url in sorted({i["url"] for i in ITEMS}):
        entries = [i for i in ITEMS if i["url"] == url]
        first = entries[0]
        record = {
            "source_title": first["source_title"], "source_url": url,
            "publisher": first["publisher"], "source_type": first["source_type"],
            "publication_date": first["publication_date"], "accessed_date": CHECKED,
            "linked_temple_ids": sorted({i["temple_id"] for i in entries}),
            "categories_with_relevant_source_content": sorted({c for i in entries for c in i["categories"]}),
            "inspection_method": "Opened the source page/PDF and inspected the cited HTML/PDF section; the relevant lines/page references are stored on each document.",
            "note": "No automated collection was run. Historical conservation entries are not represented as current condition claims.",
        }
        if url in check_by_url:
            check_by_url[url].update(record)
        else:
            checks.append(record)
    # This district-administration page was inspected as corroboration but is
    # not copied into a separate document because it substantially overlaps
    # the state-tourism doorway description above.
    district_url = "https://sonitpur.assam.gov.in/tourist-place-detail/272"
    district_check = {
        "source_title": "Da Parbatia Gate",
        "source_url": district_url,
        "publisher": "Sonitpur District Administration, Government of Assam",
        "source_type": "official_district_tourism_page",
        "publication_date": "2026-10-28 (page updated)",
        "accessed_date": CHECKED,
        "linked_temple_ids": ["asi_assam_68e3d36ac845c504"],
        "categories_with_relevant_source_content": ["location", "architecture"],
        "inspection_method": "Opened the HTML page and read the temple-specific description; the page identifies Da Parbatia Gate near Tezpur and describes the surviving doorway and early-Gupta-style carving.",
        "note": "Inspected as corroboration; substantially overlaps the state tourism doorway document and therefore no duplicate knowledge document was created.",
    }
    if district_url in check_by_url:
        check_by_url[district_url].update(district_check)
    else:
        checks.append(district_check)
    parbatia_row = queue["asi_assam_68e3d36ac845c504"]
    for key in ("sources_inspected", "previously_inspected_source_urls"):
        if district_url not in parbatia_row.setdefault(key, []):
            parbatia_row[key].append(district_url)
    district_note = "Inspected Sonitpur District Administration's Da Parbatia Gate page; it corroborates the Tezpur locality and doorway description, so no near-duplicate document was added."
    if district_note not in parbatia_row.setdefault("research_notes", []):
        parbatia_row["research_notes"].append(district_note)
    plan["last_checkpoint"] = "2026-11-05-group16"
    plan["last_updated_utc"] = datetime.now(timezone.utc).isoformat()
    docs_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    catalogue_path.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"catalogue": len(catalogue), "documents": len(docs), "documents_added": added, "source_urls_inspected": len({i['url'] for i in ITEMS})}, indent=2))


if __name__ == "__main__":
    main()
