"""Record a small, manually inspected Andhra Pradesh research checkpoint."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS_PATH = DATA / "raw" / "temple_sources.json"
PLAN_PATH = DATA / "research_plan_all_217.json"
TODAY = "2026-11-05"


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def make_doc(temple: dict, document_id: str, topic: str, title: str,
             source_title: str, source_url: str, publisher: str, source_type: str,
             text: str, publication_date: str | None = None) -> dict:
    return {
        "document_id": document_id,
        "temple_id": temple["id"],
        "temple_name": temple.get("canonical_name") or (temple.get("names") or [temple["id"]])[0],
        "state": temple.get("state"), "district": temple.get("district"),
        "topic": topic, "title": title, "source_title": source_title,
        "source_url": source_url, "publisher": publisher, "source_type": source_type,
        "language": "en", "publication_date": publication_date,
        "retrieval_date": TODAY, "collection_timestamp": datetime.now(timezone.utc).isoformat(),
        "content_hash": content_hash(text), "verification_status": "source_review_pending",
        "review_status": "pending_human_review", "is_paraphrase": True, "text": text,
    }


def main() -> None:
    catalogue = json.loads((DATA / "catalogue.json").read_text(encoding="utf-8"))
    by_id = {row["id"]: row for row in catalogue}
    docs = json.loads(DOCS_PATH.read_text(encoding="utf-8"))
    existing_ids = {row.get("document_id") for row in docs}
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))

    sources = {
        "unesco": {
            "source_title": "Sri Veerabhadra Temple and Monolithic Bull (Nandi), Lepakshi (The Vijayanagara Sculpture and Painting Art Tradition)",
            "url": "https://whc.unesco.org/en/tentativelists/6607/",
            "publisher": "UNESCO World Heritage Centre (Tentative List submission by India)",
            "source_type": "unesco_tentative_list_dossier",
            "publication_date": "2022-02-17",
        },
        "som": {
            "source_title": "Archaeological Survey of India Annual Report 1902-03: Chennakesavami Temple at Sompalle",
            "url": "https://ignca.gov.in/Asi_data/13956.pdf",
            "publisher": "Archaeological Survey of India; digitized by IGNCA",
            "source_type": "historical_asi_report_pdf",
            "publication_date": "1904",
        },
        "bicc": {
            "source_title": "Sri Golingeswara Swami Vari Temple, Biccavolu",
            "url": "https://eastgodavari.ap.gov.in/temples/sri-golingeswara-swami-vari-temple-biccavolu/",
            "publisher": "East Godavari District Administration, Government of Andhra Pradesh",
            "source_type": "official_district_administration_page",
            "publication_date": None,
        },
        "ncf": {
            "source_title": "Amaravati Circle Joint Hand: Andhra Pradesh",
            "url": "https://ncf.nic.in/joint-hand/andhra_pradesh_amravati_circle",
            "publisher": "National Culture Fund / Archaeological Survey of India project listing",
            "source_type": "official_heritage_conservation_project_listing",
            "publication_date": None,
        },
        "tuda": {
            "source_title": "Tirupati Urban Development Authority Master Plan and Zonal Development Plans 2040, Part A",
            "url": "https://www.tudaap.in/Admintuda254tuda124ttda/assets/ZDPR%20Part-A.pdf",
            "publisher": "Tirupati Urban Development Authority",
            "source_type": "regional_development_plan_pdf",
            "publication_date": None,
        },
        "ttd": {
            "source_title": "TTD Board Resolution Item 269: Proposal concerning Sri Parasurameswara Swamy Temple, Gudimallam",
            "url": "https://www.tirumala.org/BoardResolutions/74_1834.pdf",
            "publisher": "Tirumala Tirupati Devasthanams",
            "source_type": "official_temple_administration_board_resolution_pdf",
            "publication_date": "2011-01-20",
        },
        "rajya": {
            "source_title": "Rajya Sabha Unstarred Question No. 2421: List of Centrally Protected Monuments/Sites under ASI in Andhra Pradesh",
            "url": "https://rsdebate.nic.in/bitstream/123456789/725884/1/PQ_256_24032022_U2421_p152_p159.pdf",
            "publisher": "Rajya Sabha Secretariat / Government of India",
            "source_type": "official_parliamentary_answer_pdf",
            "publication_date": "2022-03-24",
        },
    }

    documents = [
        make_doc(
            by_id["asi_andhra_prade_bead535e8e3f76eb"],
            "systematic_research_20261105_lepakshi_veerabhadra_unesco_history_architecture",
            "history_architecture_inscriptions_heritage", "Lepakshi Veerabhadra Temple: development, architecture, inscriptions and tentative heritage status",
            sources["unesco"]["source_title"], sources["unesco"]["url"], sources["unesco"]["publisher"], sources["unesco"]["source_type"],
            "India's UNESCO Tentative List dossier describes the Lepakshi Veerabhadra temple complex as a multi-phase site. It proposes broad architectural phases from 1100–1350, 1350–1600 and 1600–1800 CE; the dossier associates the complex's mature Vijayanagara development with the period of Achyutaraya (1529–1542). It cautions that inscriptions do not establish the temple's early history. The dossier describes a three-shrine arrangement for Veerabhadra, Papanaseswara and Raghunatha, mandapas within successive enclosure walls, and fresco-secco paintings on plaster depicting epic and Puranic scenes. It reports about 20 inscriptions on enclosure walls, most associated with Achyutaraya's reign, and describes granite monolithic sculpture including the Nandi and Naga-sivalinga. Traditional narratives in the dossier, including the Jatayu account, are religious tradition rather than documentary history. Heritage status: this is a UNESCO Tentative List nomination submitted by India on 17 February 2022; it is not a World Heritage inscription. The dossier also records past damage to frescoes from long periods without maintenance, but it is not a current conservation-condition report. Sources: UNESCO Tentative List dossier, accessed 2026-11-05, historical narrative and component descriptions (web page; no PDF page numbers).",
            sources["unesco"]["publication_date"],
        ),
        make_doc(
            by_id["asi_andhra_prade_ba65914fa7b7de40"],
            "systematic_research_20261105_sompalle_chennakesava_asi_history_architecture",
            "history_architecture_religion_inscriptions_conservation", "Chennakesavami Temple, Sompalle: ASI report on history, structure, worship and repairs",
            sources["som"]["source_title"], sources["som"]["url"], sources["som"]["publisher"], sources["som"]["source_type"],
            "The Archaeological Survey of India's 1902–03 annual report records the local Poligar-family account of Sompalle's development and temple building; the report presents this as local tradition, not independently established chronology. Its description identifies the main image as Chennakesavami and records daily puja at the time of the report, with copper processional images of the deity and Sri Devi and Bhudevi used on festival occasions. Architecturally, the report calls the building Vijayanagara style and describes a single enclosed court, east gateway with stone lower section and brick-and-plaster superstructure, mukha mandapa, maha mandapa, ardha mandapa, kalyana mandapa, ratha-like shrine and a tall monolithic flagstaff. It notes a Telugu inscription in the utsava-image mandapa naming a donor, Krishnama Nayudu, and a cyclic-year date but the digitized passage does not securely resolve the corresponding calendar year. The report describes earlier repairs to damaged brickwork, roof leakage and structural elements; these are historical conservation observations from the early twentieth century and do not establish present condition. Report reference: pages 85–89 (printed pagination), accessed 2026-11-05. The report's historical place names and descriptions are retained as period terminology, not asserted as current administrative data.",
            sources["som"]["publication_date"],
        ),
        make_doc(
            by_id["asi_andhra_prade_d219a5f1c4c7fc35"],
            "systematic_research_20261105_biccavolu_golingeswara_architecture_inscriptions",
            "history_architecture_religion_inscriptions", "Golingeswara group at Biccavolu: Eastern Chalukya-era architecture and sculpture",
            sources["bicc"]["source_title"], sources["bicc"]["url"], sources["bicc"]["publisher"], sources["bicc"]["source_type"],
            "The East Godavari District Administration page describes Biccavolu as a group of Eastern Chalukya-period temples and dates the group broadly to the 9th–10th centuries; it uses the village's older form Birudankinavolu and associates the place with Gunaga Vijayaditya III. Its account of Golingeswara identifies a central Shiva shrine, a Sivalinga, and 33 inscriptional lines on the door jambs. It describes the mukhamandapa sculptures of Shiva with Parvati (Alingana Chandrasekhara) and Ganesha, and records named images and features in nearby Rajaraja and Chandrasekhara shrines. The page also discusses field temples and loose sculptures, but does not provide a decipherment or translation of the 33-line inscription, a festival calendar, or current visitor arrangements. The page is an official district account with no publication date shown; accessed 2026-11-05. Its broad dating and historical attribution are preserved as claims of that page and remain pending review.",
        ),
        make_doc(
            by_id["asi_andhra_prade_63f2355eafb0759e"],
            "systematic_research_20261105_hemavati_asi_conservation_listing",
            "heritage_conservation", "Hemavati Group of Old Temples: conservation work items listed by the National Culture Fund",
            sources["ncf"]["source_title"], sources["ncf"]["url"], sources["ncf"]["publisher"], sources["ncf"]["source_type"],
            "The National Culture Fund's Amaravati Circle listing includes the Group of Old Temples at Hemavati, Sri Sathya Sai District, and describes work items for the site: stucco treatment to a brick minaret over the enclosure wall and a subsidiary-shrine vimana, pointing of masonry, underpinning of a brick wall, water-tightening of sub-shrines, illumination, and replacement of an old toilet block with a pilgrim toilet block. The page is a project/work listing; it does not state when each item was completed, so these are recorded as listed conservation works rather than confirmed completed repairs. It provides no historical chronology, deity identification, inscription reading, festival details or current visitor rules. Accessed 2026-11-05; no publication date displayed.",
        ),
        make_doc(
            by_id["asi_andhra_prade_24e5a8c78a3f68e5"],
            "systematic_research_20261105_gudimallam_architecture_and_management_records",
            "architecture_heritage_conservation", "Gudimallam Parasuramesvara Temple: development-plan description and 2011 TTD proposal",
            sources["tuda"]["source_title"], sources["tuda"]["url"], sources["tuda"]["publisher"], sources["tuda"]["source_type"],
            "The Tirupati Urban Development Authority's regional plan identifies the Sri Parsurameshwara Temple at Gudimallam as a religious site, lists ASI ownership with Endowments Department functioning, and describes a stone-and-lime structure with an off-axis entrance, semi-vaulted roof and walled mandapa. The same plan labels the period as the 2nd century and style as Early Chola, while a 2011 TTD board agenda describes worship of the linga as dating to the 2nd century BCE; these source statements are not identical in scope or precision and require specialist review rather than being collapsed into a single uncontested date. The TTD agenda says maintenance was then with the Archaeology Department and proposes that TTD take over; the document alone does not establish that the proposal was carried out. The TUDA plan also notes conservation status as “GOOD” in its own assessment, which is historical and not a current condition survey. TUDA PDF page 78; TTD agenda item 269, resolution dated 2011-01-20; both accessed 2026-11-05.",
        ),
    ]

    for doc in documents:
        if doc["document_id"] not in existing_ids:
            docs.append(doc)
            existing_ids.add(doc["document_id"])
    DOCS_PATH.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Keep the catalogue's document links consistent with the raw knowledge set.
    for doc in documents:
        temple = by_id[doc["temple_id"]]
        linked = temple.setdefault("document_ids", [])
        if doc["document_id"] not in linked:
            linked.append(doc["document_id"])
    (DATA / "catalogue.json").write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checks = plan.setdefault("source_checks_this_operation", [])
    new_checks_start = len(checks)

    def check(key: str, temple_ids: list[str], categories: list[str], evidence: str, page_refs: str | None = None) -> None:
        src = sources[key]
        checks.append({
            "source_title": src["source_title"], "source_url": src["url"],
            "publisher": src["publisher"], "source_type": src["source_type"],
            "publication_date": src["publication_date"], "accessed_date": TODAY,
            "linked_temple_ids": temple_ids,
            "categories_with_relevant_source_content": categories,
            "inspection_method": "Opened and inspected the source page or PDF text; verified the matching temple name and locality.",
            "note": evidence + (f" Source page reference: {page_refs}." if page_refs else ""),
        })

    check("unesco", ["asi_andhra_prade_bead535e8e3f76eb"],
          ["historical_background", "architecture", "religious_cultural_significance", "inscriptions_historical_evidence", "heritage_conservation"],
          "Inspected the nomination dossier; status explicitly remains Tentative List, not inscription.")
    check("som", ["asi_andhra_prade_ba65914fa7b7de40"],
          ["historical_background", "architecture", "religious_cultural_significance", "festivals_traditions", "inscriptions_historical_evidence", "heritage_conservation"],
          "Inspected ASI Annual Report 1902-03 temple section; its local-origin account is identified as tradition and repairs are dated historical observations.", "printed pages 85-89")
    check("bicc", ["asi_andhra_prade_d219a5f1c4c7fc35"],
          ["historical_background", "architecture", "religious_cultural_significance", "inscriptions_historical_evidence"],
          "Inspected official East Godavari district temple page; page names Biccavolu and discusses Golingeswara, shrines, images and inscription lines.")
    check("ncf", ["asi_andhra_prade_63f2355eafb0759e", "asi_andhra_prade_d219a5f1c4c7fc35", "asi_andhra_prade_4902522d216f33d7", "asi_andhra_prade_78f1c41f21c933de"],
          ["heritage_conservation"],
          "Inspected project listing row for Hemavati and shared Biccavolu temple-group conservation entry; listed work is not treated as completed.")
    check("tuda", ["asi_andhra_prade_24e5a8c78a3f68e5"],
          ["architecture", "heritage_conservation", "visitor_information"],
          "Inspected TUDA plan PDF page 78 for Gudimallam; date/style wording and preservation status are historical plan claims.", "printed page 78")
    check("ttd", ["asi_andhra_prade_24e5a8c78a3f68e5"],
          ["historical_background", "heritage_conservation", "religious_cultural_significance"],
          "Inspected TTD board agenda item 269; its proposed transfer is not treated as proof that transfer occurred.", "agenda item 269; resolution dated 2011-01-20")
    ap_ids = [
        "asi_andhra_prade_4824bbb04f702849", "asi_andhra_prade_5509b425f6edbf42",
        "asi_andhra_prade_bead535e8e3f76eb", "asi_andhra_prade_34fdc7ad2433488f",
        "asi_andhra_prade_994f268937105045", "asi_andhra_prade_e74ff866d54d0cc2",
        "asi_andhra_prade_24e5a8c78a3f68e5", "asi_andhra_prade_85900195bd76980b",
        "asi_andhra_prade_e429b0544ae6aaa7", "asi_andhra_prade_ba65914fa7b7de40",
        "asi_andhra_prade_d219a5f1c4c7fc35", "asi_andhra_prade_4902522d216f33d7",
        "asi_andhra_prade_78f1c41f21c933de",
    ]
    check("rajya", ap_ids, ["heritage_conservation"],
          "Inspected the official parliamentary annex table and matched listed monument names to their localities; this establishes protected-list status only, not temple history or current condition.",
          "printed pages 154-156")

    # Remove accidental duplicate source checks on reruns, while retaining one checked relationship per URL/temple tuple.
    unique_checks = {}
    for source in checks:
        k = (source.get("source_url"), tuple(sorted(source.get("linked_temple_ids", []))))
        unique_checks[k] = source
    newly_inspected_checks = checks[new_checks_start:]
    checkpoint_temple_ids = sorted({tid for source in newly_inspected_checks for tid in source.get("linked_temple_ids", [])})
    plan["source_checks_this_operation"] = list(unique_checks.values())
    plan["last_checkpoint"] = {
        "checkpoint_id": "systematic_research_20261105_ap_group_01",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "temple_ids": checkpoint_temple_ids,
        "documents_added": [doc["document_id"] for doc in documents],
        "note": "Manual inspection of official/institutional pages and PDFs; no automated collection or source-registry permission changes.",
    }
    PLAN_PATH.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"documents_total": len(docs), "new_document_ids": [d["document_id"] for d in documents],
                      "source_checks": len(plan["source_checks_this_operation"]), "checkpoint_temple_links": len(plan["last_checkpoint"]["temple_ids"])}, indent=2))


if __name__ == "__main__":
    main()
