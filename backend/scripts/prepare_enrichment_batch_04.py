"""Prepare Batch 4 source-attributed profiles for human review.

This is a local-data-only preparation script: it does not fetch websites,
change source approval settings, mark facts verified, or modify ChromaDB.
Stable document IDs and content hashes make repeat runs idempotent.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CATALOGUE_PATH = DATA / "catalogue.json"
DOCS_PATH = DATA / "raw" / "temple_sources.json"
MANIFEST_PATH = DATA / "enrichment_manifest_batch_04.json"
BATCH_ID = "2026-11-05-batch-04"
TODAY = date.today().isoformat()

SOURCES = {
    "unesco_ramappa": {
        "source_title": "Kakatiya Rudreshwara (Ramappa) Temple, Telangana",
        "source_url": "https://whc.unesco.org/en/list/1570",
        "publisher": "UNESCO World Heritage Centre",
        "source_type": "international_heritage_record",
        "publication_date": None,
        "note": "Inscribed on UNESCO World Heritage List in 2021; page accessed 2026-11-05.",
    },
    "unesco_konark": {
        "source_title": "Sun Temple, Konârak",
        "source_url": "https://whc.unesco.org/en/list/246",
        "publisher": "UNESCO World Heritage Centre",
        "source_type": "international_heritage_record",
        "publication_date": None,
        "note": "Inscribed in 1984; page accessed 2026-11-05. Current conservation details are property-level and may change.",
    },
    "unesco_pattadakal": {
        "source_title": "Group of Monuments at Pattadakal",
        "source_url": "https://whc.unesco.org/en/list/239",
        "publisher": "UNESCO World Heritage Centre",
        "source_type": "international_heritage_record",
        "publication_date": None,
        "note": "Property inscribed in 1987; page accessed 2026-11-05. Some statements describe the group, not only Virupaksha Temple.",
    },
    "hampi_report": {
        "source_title": "Section II: Periodic Report on the State of Conservation of the Group of Monuments at Hampi, India, 2003",
        "source_url": "https://whc.unesco.org/document/162842",
        "publisher": "UNESCO World Heritage Centre / Archaeological Survey of India report",
        "source_type": "heritage_conservation_report",
        "publication_date": "2003",
        "note": "Historical and conservation observations are explicitly attributed to this 2003 report, not presented as current conditions.",
    },
    "unesco_modhera": {
        "source_title": "Sun Temple, Modhera and its adjoining monuments",
        "source_url": "https://whc.unesco.org/en/tentativelists/6627",
        "publisher": "UNESCO World Heritage Centre; nomination submitted by India",
        "source_type": "unesco_tentative_list_nomination",
        "publication_date": "2022-12-13",
        "note": "Tentative List nomination only; not an inscription on the World Heritage List. Claims in the nomination are attributable to the submitting State Party.",
    },
    "unesco_kanchi": {
        "source_title": "Temples of Kanchipuram",
        "source_url": "https://whc.unesco.org/en/tentativelists/6528",
        "publisher": "UNESCO World Heritage Centre; nomination submitted by India",
        "source_type": "unesco_tentative_list_nomination",
        "publication_date": "2021-04-13",
        "note": "Tentative List nomination only; not an inscription on the World Heritage List. Vaikuntaperumal-specific claims are separated from city-wide context.",
    },
    "baijnath_asi": {
        "source_title": "100 Temples of Baijnath and Sidhnath (Baijnath)",
        "source_url": "https://ignca.gov.in/Asi_data/84884.pdf",
        "publisher": "Archaeological Survey of India; digitized by Indira Gandhi National Centre for the Arts",
        "source_type": "asi_inventory_publication",
        "publication_date": None,
        "note": "ASI inventory text identifies the monument and describes inscriptions, plan, and sculpture; accessed 2026-11-05.",
    },
    "baijnath_district": {
        "source_title": "Kangra Pilgrimage",
        "source_url": "https://hpkangra.nic.in/kangra-pilgrimage/",
        "publisher": "Kangra District Administration, Government of Himachal Pradesh",
        "source_type": "government_tourism_page",
        "publication_date": None,
        "note": "Official district description accessed 2026-11-05; used for continued worship and the district's architectural summary.",
    },
    "martand_nma": {
        "source_title": "Martand Temple (National Monuments Authority meeting record, 254th meeting)",
        "source_url": "https://www.nma.gov.in/showfile.php?lang=2&level=1&lid=535&ls_id=416&nma_type=0",
        "publisher": "National Monuments Authority, Ministry of Culture, Government of India",
        "source_type": "government_monument_description",
        "publication_date": "2019-12-03",
        "note": "A brief monument description is reproduced in the meeting record. Its attribution of the temple's destruction is historically contested and is deliberately omitted from these drafts.",
    },
    "martand_district": {
        "source_title": "Martand Sun Temple",
        "source_url": "https://anantnag.nic.in/tourist-place/martand-sun-temple/",
        "publisher": "Anantnag District Administration, Government of Jammu and Kashmir",
        "source_type": "government_tourism_page",
        "publication_date": None,
        "note": "Official district visitor/location page accessed 2026-11-05; it does not provide detailed visitor schedules or current access conditions.",
    },
}

# Each document is a coherent topic profile with a single direct source. The
# information is paraphrased narrowly; a source may represent a nomination or
# historical report rather than a current survey.
RECORDS = [
    {
        "temple_id": "konark",
        "missing_topics": ["architectural composition", "sculptural programme", "worship/festival", "conservation history"],
        "source_keys": ["unesco_konark"],
        "documents": [
            ("history_patrons", "Konark: 13th-century Surya sanctuary and historical setting", "unesco_konark",
             "UNESCO dates the Sun Temple at Konârak to the 13th century and frames it as an outstanding testimony to the 13th-century kingdom of Orissa. The UNESCO account connects the monument to the spread of Surya worship to eastern India. It also records an inscribed property of 10.62 hectares in Puri District and an inscription date of 1984. The page separately recounts a dramatic construction story involving a master builder and his son; that account is presented there as legend, not as established construction history, and is not used here as fact."),
            ("architecture_chariot_plan", "Konark: the solar chariot and surviving temple spaces", "unesco_konark",
             "UNESCO describes the monument as a monumental representation of Surya's chariot, with 24 decorated wheels and a team of six horses. Its architectural account identifies the surviving Jagamohana (audience hall) and the temple's sculptural integration with the built form; the principal sanctuary tower (vimana) no longer survives. This profile distinguishes surviving fabric from the larger original conception and does not assume that every element remains intact."),
            ("sculpture_iconography", "Konark: sculpture as architecture and narrative", "unesco_konark",
             "UNESCO treats Konark's sculpture and architecture as an integrated artistic programme: sculptural relief is part of the monument's form, design and narrative effect. The property retains surviving structures and sculptures as well as displaced remains preserved in situ. UNESCO also associates the site's cultural continuity with living practices, including the Chandrabhaga festival. This source does not provide a current festival calendar, ritual sequence or event schedule."),
            ("heritage_conservation", "Konark: heritage status, protection and conservation concerns", "unesco_konark",
             "The Sun Temple at Konârak was inscribed on the UNESCO World Heritage List in 1984. UNESCO states that it is protected under India's Ancient Monuments and Archaeological Sites and Remains framework and that conservation programmes are undertaken by the Archaeological Survey of India. Its property record identifies historical structural concerns and environmental pressures, and calls for continuing structural and material conservation of the Jagamohana and sculptures. These are the concerns recorded on the UNESCO page; they should not be read as a real-time condition assessment."),
        ],
    },
    {
        "temple_id": "asi_telangana_f3a7458053e48f24",
        "missing_topics": ["construction history", "building technology", "sculpture/dance", "heritage and ritual"],
        "source_keys": ["unesco_ramappa"],
        "documents": [
            ("history_kakatiya_patronage", "Ramappa: Kakatiya period, patrons and construction chronology", "unesco_ramappa",
             "UNESCO places Rudreshwara, popularly called Ramappa, within the Kakatiya period (1123–1323 CE) and associates the walled complex with rulers Rudradeva and Recharla Rudra. It dates the beginning of the sandstone temple's construction to 1213 CE and says work is believed to have continued for about four decades. The source names the principal shrine as a Shiva temple. These are UNESCO's documented chronology and attribution; the document does not infer a precise completion year."),
            ("architecture_engineering", "Ramappa: materials, vimana and construction engineering", "unesco_ramappa",
             "UNESCO describes sandstone construction, decorated beams and pillars carved from granite and dolerite, and a distinctive pyramidal, horizontally stepped vimana. Its roof structure uses lightweight porous bricks, popularly called floating bricks, to reduce weight. The UNESCO Outstanding Universal Value account also describes experimentation with a sandbox foundation and material selection as part of the site's engineering significance. The terms here follow UNESCO's interpretation and do not claim that a single technique alone explains the temple's structural performance."),
            ("sculpture_dance_culture", "Ramappa: bracket figures, stone carving and dance imagery", "unesco_ramappa",
             "UNESCO highlights the temple's hard dolerite carvings, especially bracket figures, for their finely worked surfaces and sense of movement. The sculptural programme depicts regional dance customs and Kakatiya cultural forms, including figures and motifs identified in UNESCO's evaluation. Rather than treating these images as a complete record of historical dance, this profile describes them as visual evidence interpreted by UNESCO as expressing local artistic and cultural traditions."),
            ("heritage_setting_ritual", "Ramappa: World Heritage recognition, landscape and living practice", "unesco_ramappa",
             "The Kakatiya Rudreshwara Temple was inscribed on the UNESCO World Heritage List in 2021. UNESCO presents its heritage value through the relationship among temple architecture, sculpture, ritual, dance and the surrounding landscape, including agricultural land and the Kakatiya-built Ramappa Cheruvu reservoir. UNESCO also describes the complex as a living Shaiva temple where ceremonies continue. The page says the Archaeological Survey of India has maintained and conserved the protected monument since its identification as protected in 1914; this is the source's account, not an independent condition audit."),
        ],
    },
    {
        "temple_id": "asi_karnataka_7c32bc783d1664dc",
        "missing_topics": ["Chalukya context", "Virupaksha patronage", "regional architectural synthesis", "heritage status"],
        "source_keys": ["unesco_pattadakal"],
        "documents": [
            ("history_chalukya_context", "Pattadakal Virupaksha: Chalukya-era patronage", "unesco_pattadakal",
             "UNESCO places the Virupaksha Temple within the 7th- and 8th-century Chalukya monuments at Pattadakal. It dates the temple to about 740 CE and attributes its construction to Queen Lokamahadevi, who commissioned it to commemorate her husband's victory over southern rulers. The source describes Virupaksha as a prominent monument within the wider group; this short chronology is based on UNESCO's group record and does not add a more precise building sequence."),
            ("architecture_north_south_synthesis", "Pattadakal Virupaksha: architectural setting within the monument group", "unesco_pattadakal",
             "UNESCO characterizes Pattadakal as an eclectic artistic centre where architectural forms associated with northern and southern India were brought into a harmonious blend under Chalukya patronage. The property includes a series of nine Hindu temples and a Jain sanctuary, with Virupaksha singled out as a masterpiece. The description is group-level: it supports the temple's place in Pattadakal's architectural setting, but does not assign every stylistic feature of all ten monuments to Virupaksha alone."),
        ],
    },
    {
        "temple_id": "whc_b5eaf9ee03e0215d1573",
        "missing_topics": ["founding and royal context", "temple plan", "inscription and urban setting"],
        "source_keys": ["hampi_report"],
        "documents": [
            ("history_krishnadevaraya", "Krishna Temple at Hampi: foundation and royal context", "hampi_report",
             "The 2003 UNESCO/ASI periodic report dates the Krishna Temple to 1513 and associates its construction with Vijayanagara ruler Krishnadevaraya. The report notes an inscribed account that the Balakrishna image enshrined at the temple had been brought from Udayagiri in present-day Odisha. This document reports what the historical conservation dossier records; it does not infer that the present image or all current worship practices are unchanged from the period described."),
            ("architecture_shrines", "Krishna Temple at Hampi: shrine sequence and subsidiary spaces", "hampi_report",
             "The 2003 UNESCO/ASI report describes a temple sequence comprising sanctum, vestibule, circumambulatory passage, maha-mantapa and ardha-mantapa. It also records a Devi shrine to the north and a sacred tank within the complex. The description is useful for understanding the plan documented by the report, while its date means that present access, condition and management should be checked separately."),
            ("inscription_bazaar_context", "Krishna Temple at Hampi: inscriptions and the associated market", "hampi_report",
             "The 2003 UNESCO/ASI report links the Krishna Temple to an inscription about the installation of the Balakrishna image and records a bazaar beside the temple, including references to market activity in the historical urban setting. The document preserves the report's evidence about the relationship between a sacred complex and commercial space at Hampi. It does not claim that the historical market continues today."),
        ],
    },
    {
        "temple_id": "whc_5a482f12eb769406674c",
        "missing_topics": ["Vijayanagara-era development", "temple layout", "documented conservation"],
        "source_keys": ["hampi_report"],
        "documents": [
            ("history_vijayanagara", "Pattabhirama Temple at Hampi: date and historical setting", "hampi_report",
             "The UNESCO/ASI periodic report describes Pattabhirama as a 16th-century Vijayanagara temple complex and identifies it as one of the largest temple enclosures at Hampi. Its account places the temple in the wider sacred and urban landscape of the Vijayanagara capital. This is a period attribution from a 2003 conservation report; it does not establish a precise foundation year or identify a named patron where the cited passage does not do so."),
            ("architecture_mandapas", "Pattabhirama Temple at Hampi: courtyard and pillared halls", "hampi_report",
             "The 2003 UNESCO/ASI report describes Pattabhirama's spacious courtyard, eastern tower, large pillared halls and kalyana-mantapa. It places these halls within a large Vijayanagara-period enclosure, whose scale and open courtyard distinguish the complex's overall plan in the report. These features form the basis of this profile's architectural account. The report describes the complex as a whole and the document avoids claiming a specific ritual use for every hall unless the report names it. The source does not establish that all structures have remained in the same condition since the survey."),
            ("conservation_2003", "Pattabhirama Temple at Hampi: conservation recorded in 2003", "hampi_report",
             "In its 2003 conservation account, the UNESCO/ASI report records work at Pattabhirama that included floor pointing, roof water-tightening, replacement of broken beams in the maha-mantapa, work on the circumambulatory-path floor, and repairs to navaranga pillars and beams. These are dated interventions documented in 2003. They should not be interpreted as a report of current structural condition or as evidence that the same work remains adequate today."),
        ],
    },
    {
        "temple_id": "whc_0550440746a0ab1b40e6",
        "missing_topics": ["chronological range", "architectural typology", "pre-Vijayanagara context"],
        "source_keys": ["hampi_report"],
        "documents": [
            ("history_pre_vijayanagara", "Hemakuta at Hampi: an early and long-lived sacred landscape", "hampi_report",
             "The 2003 UNESCO/ASI periodic report describes Hemakuta as a group that includes temples spanning approximately the 9th through 16th centuries, with parts of the sacred landscape predating the main Vijayanagara urban phase. The report identifies the group as a large complex with substantial boundary walls and gateways. It therefore should not be assigned a single construction date or treated as one uniform building campaign."),
            ("architecture_temple_types", "Hemakuta at Hampi: temple forms and the Prasanna Virupaksha shrine", "hampi_report",
             "The 2003 UNESCO/ASI report notes single-, double- and triple-celled temple plans within the Hemakuta group. It identifies the Prasanna Virupaksha shrine as having a Kadamba-Nagara superstructure and records a date of 1338 for that shrine. These architectural and dating details apply to the named component and typologies described in the report, not automatically to every Hemakuta structure."),
        ],
    },
    {
        "temple_id": "asi_gujarat_fd7e0734b68a92df",
        "missing_topics": ["Solanki-era context", "architectural sequence", "sculptural programme", "heritage status"],
        "source_keys": ["unesco_modhera"],
        "documents": [
            ("history_solar_worship", "Modhera Sun Temple: historical attribution and solar dedication", "unesco_modhera",
             "The Indian State Party's UNESCO Tentative List nomination presents Modhera as a Surya temple and places it within Gujarat's Solanki-period architectural heritage. The nomination associates its style with the 11th-century Maru-Gurjara tradition and discusses Bhima I as the historical context; its dating is stylistic rather than a securely stated construction year. Because the page is a national nomination, its claims are attributed to that submission. Modhera is on UNESCO's Tentative List, not the World Heritage List."),
            ("architecture_ensemble", "Modhera Sun Temple: shrine, assembly hall and sacred tank", "unesco_modhera",
             "The Tentative List nomination describes an ensemble of a principal shrine with a gudhamandapa, a separate Sabhamandapa or assembly hall, and a sacred tank called Ramakunda or Suryakunda in the same account. The buildings sit on a paved platform, with the hall distinct from the main shrine and the tank in front. The description records an east-facing layout and yellow sandstone. This profile follows the nomination and does not imply that every part survives in its original complete form."),
            ("sculpture_iconography", "Modhera Sun Temple: Surya imagery and carved architectural surfaces", "unesco_modhera",
             "The Indian nomination describes Surya figures as prominent in the temple's sculptural scheme, including figures placed in niches around the circumambulatory passage and on shrine walls. It also records deities, dancers and narrative imagery across architectural surfaces, with the twelve Adityas among the named iconographic groups. The page describes the Sabhamandapa as an open pillared hall with an octagonal central arrangement and carved surfaces. These claims are attributed to India's Tentative List submission."),
            ("heritage_conservation_tentative", "Modhera Sun Temple: heritage nomination and conservation account", "unesco_modhera",
             "India submitted the Modhera and adjoining monuments property to UNESCO's Tentative List in December 2022. This is a nomination status, not World Heritage inscription. The nomination says the Archaeological Survey of India is responsible for conservation and describes protected areas under India's monuments framework. Those statements reflect the submitted nomination; this document does not provide a current condition survey, visitor timetable or a dated inventory of recent conservation work."),
        ],
    },
    {
        "temple_id": "asi_tamil_nadu_e53edf8ca8494828",
        "missing_topics": ["Pallava chronology", "three-level shrine plan", "sculpture and inscriptions", "Vaishnava significance"],
        "source_keys": ["unesco_kanchi"],
        "documents": [
            ("history_pallava_patronage", "Vaikuntaperumal: Pallava patronage and Kanchipuram context", "unesco_kanchi",
             "The Indian nomination for the Temples of Kanchipuram identifies Paramesvara Vinnagaram, also called Vaikuntaperumal, as one of the city's nominated monuments. It places the shrine in Pallava Kanchipuram and associates its construction with Pallava ruler Nandivarman II Pallavamalla (731–796 CE). The same submission describes Kanchipuram as a major religious and political centre that later remained important under the Cholas. The city-wide context is not specific to this temple alone."),
            ("architecture_three_levels", "Vaikuntaperumal: stacked sanctums and architectural plan", "unesco_kanchi",
             "The Kanchipuram nomination describes Vaikuntaperumal's unusual three-level shrine arrangement, with Vishnu shown in seated, reclining and standing forms on successive levels. It calls the vimana an ashtanga form and describes a surrounding mandapa and sculptural cloister. These details come from the Indian Tentative List account. The source does not provide a current access guide to the upper levels, so the document makes no claim about visitor access."),
            ("sculpture_inscriptions", "Vaikuntaperumal: cloister reliefs and Pallava inscriptions", "unesco_kanchi",
             "The nomination describes narrative reliefs along the inner cloister that present a sequence associated with the Pallava dynasty. It notes that captions or labels carved with the panels help identify figures and events, and records Pallava inscriptions associated with the temple, including an early inscription from the reign of Nandivarman II. The nomination also reports later grants connected to Vaishnava worship. Its dynastic visual narrative includes legendary ancestry; the reliefs should not be treated by themselves as independent proof of every genealogical claim."),
            ("religious_significance_heritage", "Vaikuntaperumal: Vaishnava worship and tentative heritage status", "unesco_kanchi",
             "The Kanchipuram nomination includes Vaikuntaperumal among the city's important Vaishnava temples and notes that several Vishnu shrines in Kanchipuram were praised by Alvar saints. Its temple-specific discussion associates the shrine with the Vaishnava tradition, while the city's broader religious history is shared by Shaiva, Vaishnava, Buddhist and Jain communities. The group of Kanchipuram temples is on UNESCO's Tentative List; it is not an inscribed World Heritage property. The nomination does not establish the temple's current festival calendar."),
        ],
    },
    {
        "temple_id": "asi_himachal_pra_d0cbd9e9b4b403a2",
        "missing_topics": ["inscriptional foundation history", "Nagara plan", "sculptural programme", "religious use"],
        "source_keys": ["baijnath_asi", "baijnath_district"],
        "documents": [
            ("history_inscriptions", "Baijnath: foundation recorded in Sanskrit inscriptions", "baijnath_asi",
             "The Archaeological Survey of India inventory describes two extensive Sarada-script inscriptions, composed in Sanskrit verse, that refer to the temple's construction around 1204 CE by two wealthy merchants from Kiragrama. The inventory identifies the shrine with Shiva Vaidyanatha and describes it as an important sacred monument of the Beas valley. The Kangra district administration separately says the present shrine replaced an earlier Shiva temple on the spot. The surviving inscriptional evidence supports the present temple's medieval foundation; it does not establish the date of the earlier shrine."),
            ("architecture_sculpture", "Baijnath: Nagara shikhara, mandapa and sculptural imagery", "baijnath_asi",
             "The ASI inventory describes a sanctum surmounted by a Nagara-style shikhara, a front mandapa with a low pyramidal roof, and a porch. It records a Nandi figure beneath a canopy supported by four stone pillars. The inventory also names sculptures of Shiva-Gangadhara, Ganesha, Karttikeya and Bhairava. These details are specific to the main Baijnath temple and come from the ASI's monument description."),
            ("worship_context", "Baijnath: Shiva worship and continuing religious use", "baijnath_district",
             "The Kangra District Administration states that the Baijnath temple has remained under worship since its construction in 1204 CE. It describes the sanctum's self-manifested Shiva linga, the vestibule and square mandapa, balconies to the north and south, and Nandi shrine at the porch. The district page reflects the local religious description of the linga as svayambhu and does not provide a current festival schedule. The source's present-tense account was accessed on 2026-11-05."),
        ],
    },
    {
        "temple_id": "asi_jammu_and_ka_1f8a290d8729fbea",
        "missing_topics": ["Karkota-period attribution", "architectural composition", "sculptural programme", "current conservation/access"],
        "source_keys": ["martand_nma", "martand_district"],
        "documents": [
            ("history_lalitaditya", "Martand Sun Temple: Lalitaditya-era attribution", "martand_nma",
             "A monument description reproduced by India's National Monuments Authority attributes Martand Sun Temple to Lalitaditya (724–761 CE). It locates the ruins in Anantnag District near Mattan. This is a government monument summary, rather than an inscription transcription or a full archaeological report; the attribution is therefore preserved as the NMA's stated account. A historical claim in the same summary about the temple's destruction is disputed in scholarship and has been omitted from this profile."),
            ("architecture_plan_sculpture", "Martand: courtyard plan, shrine sequence and sculptural niches", "martand_nma",
             "The National Monuments Authority description says the temple stands on a high plinth within a rectangular courtyard lined by cells and faces west. It describes a main shrine sequence of sanctum, vestibule and mandapa approached by a monumental stair. The platform niches are said to contain images including Surya, Brahma, Vishnu, Shiva, Parvati, Ganga, Yamuna and directional deities. The source describes the monument as largely ruined; this profile does not infer the original roof or details that no longer survive."),
            ("location_heritage_access", "Martand: location and limits of available visitor information", "martand_district",
             "The Anantnag District Administration identifies Martand as a tourist place in Anantnag District and describes its setting as a ruin of the Sun Temple. The district page is useful for broad location and visitor orientation, but does not establish current opening hours, access restrictions, services or conservation condition. Visitors should check current local notices before travel; this statement is a limit of the available source rather than an itinerary or access guarantee."),
        ],
    },
]


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    catalogue = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
    documents = json.loads(DOCS_PATH.read_text(encoding="utf-8"))
    coverage = json.loads((DATA / "knowledge_coverage_report.json").read_text(encoding="utf-8"))
    cat_by_id = {item.get("id"): item for item in catalogue}
    doc_ids = {item.get("document_id") for item in documents}
    old_manifests = [DATA / f"enrichment_manifest_batch_{i:02}.json" for i in range(1, 4)]
    prior_ids: set[str] = set()
    for path in old_manifests:
        old = json.loads(path.read_text(encoding="utf-8"))
        for row in old.get("temples", []):
            if row.get("temple_id"):
                prior_ids.add(row["temple_id"])
        prior_ids.update(old.get("scope_temple_ids", []))
        prior_ids.update(old.get("counts", {}).get("scope_temple_ids", []))

    target_ids = [row["temple_id"] for row in RECORDS]
    if len(target_ids) != 10 or len(set(target_ids)) != 10:
        raise SystemExit("Batch must contain exactly 10 distinct existing temple IDs")
    missing = sorted(set(target_ids) - set(cat_by_id))
    if missing:
        raise SystemExit(f"Refusing batch: temple IDs missing from catalogue: {missing}")
    overlap = sorted(set(target_ids) & prior_ids)
    if overlap:
        raise SystemExit(f"Refusing batch: temples already in a prior batch: {overlap}")

    baseline_by_id = {row.get("temple_id"): row for row in coverage.get("temples", [])}
    existing_counts = {tid: sum(1 for d in documents if d.get("temple_id") == tid) for tid in target_ids}
    new_documents: list[dict] = []
    manifest_temples: list[dict] = []
    for record in RECORDS:
        temple = cat_by_id[record["temple_id"]]
        name = temple.get("canonical_name") or (temple.get("names") or [record["temple_id"]])[0]
        temple_doc_ids: list[str] = []
        for topic, title, source_key, text in record["documents"]:
            source = SOURCES[source_key]
            doc_id = f"enrich_batch04_{record['temple_id']}_{topic}"
            normalized = " ".join(text.split())
            content_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            doc = {
                "document_id": doc_id,
                "temple_id": record["temple_id"],
                "temple_name": name,
                "state": temple.get("state"),
                "district": temple.get("district"),
                "topic": topic,
                "title": title,
                "source_title": source["source_title"],
                "source_url": source["source_url"],
                "publisher": source["publisher"],
                "source_type": source["source_type"],
                "language": "en",
                "publication_date": source["publication_date"],
                "retrieval_date": TODAY,
                "collection_timestamp": datetime.now(timezone.utc).isoformat(),
                "content_hash": content_hash,
                "verification_status": "source_review_pending",
                "review_status": "pending_human_review",
                "is_paraphrase": True,
                "text": normalized,
            }
            if not doc["source_url"].startswith("https://") or len(normalized) < 350:
                raise SystemExit(f"Invalid source URL or short document: {doc_id}")
            if doc_id in doc_ids:
                old = next(d for d in documents if d.get("document_id") == doc_id)
                if old.get("content_hash") != content_hash:
                    raise SystemExit(f"Stable ID collision with changed content: {doc_id}")
            else:
                new_documents.append(doc)
                doc_ids.add(doc_id)
            temple_doc_ids.append(doc_id)

        baseline = baseline_by_id.get(record["temple_id"], {})
        manifest_temples.append({
            "temple_id": record["temple_id"],
            "name": name,
            "state": temple.get("state"),
            "district": temple.get("district"),
            "coverage_class_before": baseline.get("coverage_class"),
            "current_documents_before": existing_counts[record["temple_id"]],
            "missing_topics_before": record["missing_topics"],
            "sources_actually_checked": [SOURCES[key] for key in record["source_keys"]],
            "document_ids": temple_doc_ids,
            "topics_prepared": [d[0] for d in record["documents"]],
            "enrichment_status": "pending_human_review",
            "source_notes": [SOURCES[key]["note"] for key in record["source_keys"]],
        })

    if new_documents:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(CATALOGUE_PATH, DATA / f"catalogue.json.batch04_backup_{stamp}")
        shutil.copy2(DOCS_PATH, DATA / "raw" / f"temple_sources.json.batch04_backup_{stamp}")
        documents.extend(new_documents)
        for doc in new_documents:
            temple = cat_by_id[doc["temple_id"]]
            if doc["document_id"] not in temple.setdefault("document_ids", []):
                temple["document_ids"].append(doc["document_id"])
            source_entry = {"title": doc["source_title"], "url": doc["source_url"], "publisher": doc["publisher"]}
            if source_entry not in temple.setdefault("sources", []):
                temple["sources"].append(source_entry)
        write_json(DOCS_PATH, documents)
        write_json(CATALOGUE_PATH, catalogue)

    all_sources = {key: SOURCES[key] for row in RECORDS for key in row["source_keys"]}
    manifest = {
        "batch_id": BATCH_ID,
        "created_date": TODAY,
        "scope": "10 existing undercovered catalogue temples, selected outside the first three enrichment batch scopes; no new catalogue entries",
        "selection_basis": "Current coverage report (170 basic, 39 limited, 8 moderate, 0 comprehensive across 217 temples), source availability, and no temple-ID overlap with batches 01-03.",
        "collection_method": "Manual access to the listed institutional sources; no automated bulk collection; source registry and approval gates unchanged.",
        "counts": {
            "temples_in_batch": len(RECORDS),
            "new_documents_appended_this_run": len(new_documents),
            "documents_in_batch": sum(len(row["documents"]) for row in RECORDS),
            "pending_human_review": sum(len(row["documents"]) for row in RECORDS),
            "automated_collection_runs": 0,
        },
        "sources_actually_checked": list(all_sources.values()),
        "temples": manifest_temples,
        "limitations": [
            "Coverage classes are heuristic and do not demonstrate factual completeness.",
            "UNESCO Tentative List pages for Modhera and Kanchipuram represent nominations submitted by India; neither is described as an inscribed World Heritage property in these documents.",
            "The Hampi source is a 2003 UNESCO/ASI periodic report; conservation statements are dated historical records.",
            "The Martand NMA summary contains a disputed destruction attribution; that claim is omitted pending scholarly review.",
            "No Batch 4 document is marked verified; every new document remains pending human review.",
            "Current festival calendars, visitor schedules, access conditions and live conservation status are not supplied unless explicitly cited.",
        ],
    }
    write_json(MANIFEST_PATH, manifest)
    print(json.dumps({
        "catalogue_records": len(catalogue),
        "knowledge_documents": len(documents),
        "selected_temples": len(RECORDS),
        "new_documents_appended": len(new_documents),
        "documents_pending_human_review": manifest["counts"]["pending_human_review"],
        "sources_checked": len(all_sources),
        "prior_batch_overlap": len(overlap),
        "backup_created": bool(new_documents),
        "manifest": str(MANIFEST_PATH),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
