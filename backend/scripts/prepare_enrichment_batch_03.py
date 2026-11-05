"""Append a small, source-attributed temple enrichment batch for human review.

The content below was manually prepared from the institutional pages listed in
each record. This script does not fetch pages, alter source approvals, or mark
content verified. Stable IDs make a repeat invocation a no-op after first run.
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
MANIFEST_PATH = DATA / "enrichment_manifest_batch_03.json"
BATCH_ID = "2026-11-05-batch-03"
TODAY = date.today().isoformat()

UNESCO_KHAJURAHO = {
    "source_title": "Khajuraho Group of Monuments",
    "source_url": "https://whc.unesco.org/en/list/240/",
    "publisher": "UNESCO World Heritage Centre",
    "source_type": "international_heritage_record",
}
UNESCO_MAHABODHI = {
    "source_title": "Mahabodhi Temple Complex at Bodh Gaya",
    "source_url": "https://whc.unesco.org/en/list/1056/",
    "publisher": "UNESCO World Heritage Centre",
    "source_type": "international_heritage_record",
}
UNESCO_CHOLA = {
    "source_title": "Great Living Chola Temples",
    "source_url": "https://whc.unesco.org/en/list/250/",
    "publisher": "UNESCO World Heritage Centre",
    "source_type": "international_heritage_record",
}
UNESCO_MAHABALIPURAM = {
    "source_title": "Group of Monuments at Mahabalipuram",
    "source_url": "https://whc.unesco.org/en/list/249/",
    "publisher": "UNESCO World Heritage Centre",
    "source_type": "international_heritage_record",
}
HAMPI_REPORT = {
    "source_title": "Section II: Periodic Report on the State of Conservation of the Group of Monuments at Hampi, India, 2003",
    "source_url": "https://whc.unesco.org/document/162842",
    "publisher": "UNESCO World Heritage Centre / Archaeological Survey of India report",
    "source_type": "heritage_conservation_report",
}
MADURAI_TEMPLE = {
    "source_title": "Sri Meenakshi - Sundareswarar Temple",
    "source_url": "https://madurai.nic.in/tourist-place/sri-meenakshi-sundareswarar-temple/",
    "publisher": "Madurai District Administration, Government of Tamil Nadu",
    "source_type": "government_tourism_page",
}
MADURAI_FESTIVALS = {
    "source_title": "Festivals and Events",
    "source_url": "https://madurai.nic.in/festivals-and-events/",
    "publisher": "Madurai District Administration, Government of Tamil Nadu",
    "source_type": "government_tourism_page",
}
KASHI_DISTRICT = {
    "source_title": "Shree Kashi Vishvanath Temple",
    "source_url": "https://varanasi.nic.in/tourist-place/shri-kashi-vishwanath-temple/",
    "publisher": "Varanasi District Administration, Government of Uttar Pradesh",
    "source_type": "government_tourism_page",
}

# Claim scope is intentionally narrow. Each document stays tied to the one
# institutional source that supports its statements.
RECORDS = [
    {
        "temple_id": "whc_b64d0b1bb2989639c1f1",
        "missing_topics": ["architecture", "religious significance", "sculptural/architectural details"],
        "sources_checked": [UNESCO_MAHABODHI],
        "documents": [
            ("history_religious_significance", "Mahabodhi: historical and religious setting", UNESCO_MAHABODHI,
             "UNESCO identifies Bodh Gaya as one of four holy sites associated with the life of the Buddha, particularly his enlightenment. It records an earliest temple commissioned by Emperor Asoka in the 3rd century BCE and dates the present temple to the 5th–6th centuries CE. The complex also preserves evidence of worship and sanctuary-building over a long period. These statements describe the UNESCO property and its documented history; they do not establish details of every later ritual."),
            ("architecture", "Mahabodhi: temple form and sacred precinct", UNESCO_MAHABODHI,
             "UNESCO describes the present main temple as an early surviving brick Buddhist temple of the late Gupta period. Its account identifies a roughly 50-metre temple, the Vajrasana and sacred Bodhi Tree, six other sacred sites associated with enlightenment, and ancient votive stupas within the protected enclosure; the Lotus Pond lies outside the enclosure to the south. It also describes a curvilinear tower, or shikhara, with an amalaka and kalasha, and Buddha images in niches. This architectural summary follows UNESCO's description of the listed complex."),
        ],
    },
    {
        "temple_id": "whc_798b3d431ca45563a0f8",
        "missing_topics": ["architecture", "sculpture", "heritage management"],
        "sources_checked": [UNESCO_KHAJURAHO],
        "documents": [
            ("history_architecture", "Khajuraho: Chandella period and Nagara design", UNESCO_KHAJURAHO,
             "UNESCO presents Khajuraho as a culmination of northern Indian temple art under the Chandella rulers of the 10th and 11th centuries CE. The listed group comprises 23 temples, including one partly excavated structure, in western, eastern and southern clusters. UNESCO describes the temples as sandstone buildings on ornate raised platforms, with a sanctum tower and subsidiary miniature spires characteristic of the Nagara form. The plan moves through porch, hall, vestibule and sanctum, with circumambulatory paths in some examples."),
            ("sculpture_heritage_management", "Khajuraho: sculptural programme and protection", UNESCO_KHAJURAHO,
             "UNESCO describes sculpture as integrated with Khajuraho's architecture: carved surfaces include sacred and secular motifs, worship, deities, domestic life, teachers, dancers and musicians. The UNESCO record states that the property was inscribed in 1986. It identifies Government of India ownership and Archaeological Survey of India management under the national monuments legislation, with regulated and prohibited zones around designated monuments. These are property-level heritage and management facts, not a claim that every individual temple has the same sculptures or conservation condition."),
        ],
    },
    {
        "temple_id": "whc_ffb69144fee941fb01a9",
        "missing_topics": ["history", "architecture", "worship and heritage"],
        "sources_checked": [HAMPI_REPORT],
        "documents": [
            ("history_architecture_religion", "Virupaksha at Hampi: expansion and living worship", HAMPI_REPORT,
             "The UNESCO/ASI periodic report describes Virupaksha, also called Pampapati, as Hampi's most sacred living monument. It says the complex began as a small shrine and expanded to its present dimensions in the first half of the 16th century. The report describes two large courts within a rectangular enclosure, towered gateways, and a sequence of sanctum, vestibule, ardha-mantapa and large maha-mantapa. It records that Krishnadevaraya built the smaller eastern gopura and painted pillared ranga-mantapa in 1510, and identifies the sanctum image as a Shiva linga called Virupaksha. The ceiling paintings in the ranga-mantapa are identified as Vijayanagara-period."),
        ],
    },
    {
        "temple_id": "whc_0601b84399076df5f6eb",
        "missing_topics": ["history", "architecture", "iconography", "conservation"],
        "sources_checked": [HAMPI_REPORT],
        "documents": [
            ("history_architecture", "Vitthala at Hampi: Vijayanagara expansion and plan", HAMPI_REPORT,
             "The UNESCO/ASI periodic report calls the Vitthala complex a high point of Vijayanagara art and architecture. It records that a core existed in the reign of Devaraya II (1422–1446) and that Krishnadevaraya (1509–1529) made substantial additions. The described complex includes a main shrine for Vitthala, a devi shrine, kalyana-mantapa, utsava-mantapa, a hundred-pillared mantapa and the stone chariot. The main shrine plan includes sanctum, vestibule, a closed circumambulatory path, open maha-mantapa and ardha-mantapa."),
            ("sculpture_conservation", "Vitthala at Hampi: carved pillars and documented conservation", HAMPI_REPORT,
             "The UNESCO/ASI report describes the Vitthala assembly hall's composite granite pillars with rearing animals and riders, and clusters of slender subsidiary pillars. It notes that gently tapped small pillars produce musical notes. In its 2003 conservation account, the report documents structural work at the Vitthala entrance and shrine, including strengthening broken lintel and beams and stabilizing masonry at the gopura. This is a dated record of work reported in 2003, not a statement of present condition."),
        ],
    },
    {
        "temple_id": "whc_57e81c99363e3334087c",
        "missing_topics": ["historical contributors", "architecture", "urban setting and inscriptions"],
        "sources_checked": [HAMPI_REPORT],
        "documents": [
            ("history_architecture_urban_context", "Achyutaraya at Hampi: patronage, plan and bazaar", HAMPI_REPORT,
             "The UNESCO/ASI periodic report dates the Achyutaraya (Tiruvengalanatha) temple to 1534 and attributes its construction to Hiriya Tirumalaraja Wodeyar, a mahamandaleshwara serving under Achutadevaraya. It describes a north-facing temple within a double enclosure, a spacious courtyard, and a long bazaar called Achyutarayapete. The report gives the inner plan as sanctum, vestibule, ardha-mantapa and ornate maha-mantapa. It also records an inscriptional reference to a weekly Tuesday market; this is evidence reported in the source, not a claim about present market activity."),
        ],
    },
    {
        "temple_id": "asi_tamil_nadu_9b2980bb768b7c42",
        "missing_topics": ["history", "architecture", "sculpture", "heritage status"],
        "sources_checked": [UNESCO_CHOLA],
        "documents": [
            ("history_architecture_heritage", "Gangaikondacholapuram: Rajendra I and Chola architecture", UNESCO_CHOLA,
             "UNESCO states that Rajendra I (1012–1044 CE) built the Brihadisvara temple at Gangaikondacholapuram for Shiva. It describes exceptional sculpture and identifies the bronzes of Bhogasakti and Subrahmanya as notable Chola metal icons. UNESCO places the temple within the Great Living Chola Temples property and regards the three temples at Thanjavur, Gangaikondacholapuram and Darasuram as outstanding evidence of Chola architecture and ideology. The source does not establish details of current festival schedules."),
        ],
    },
    {
        "temple_id": "brihadeeswarar",
        "missing_topics": ["architecture detail", "sculpture and inscriptions", "heritage context"],
        "sources_checked": [UNESCO_CHOLA],
        "documents": [
            ("architecture_heritage", "Brihadisvara at Thanjavur: Dravida form and Chola heritage", UNESCO_CHOLA,
             "UNESCO describes the Thanjavur Brihadisvara as the first great example in the development represented by the Great Living Chola Temples, an outstanding creative achievement in the pure Dravida form. The property is recognized as testimony to the development of Chola architecture and Tamil civilization. This document adds UNESCO's property-level architectural and heritage framing; it does not repeat unverified construction measurements from secondary sources."),
        ],
    },
    {
        "temple_id": "shore",
        "missing_topics": ["history", "architecture", "heritage management"],
        "sources_checked": [UNESCO_MAHABALIPURAM],
        "documents": [
            ("history_architecture_heritage", "Shore Temple: structural Pallava architecture at Mahabalipuram", UNESCO_MAHABALIPURAM,
             "UNESCO situates the Shore Temple within the Pallava monument group at Mahabalipuram, created by a dynasty that ruled the area from the 6th to 9th centuries CE. The group includes rock-cut caves, monolithic temples, reliefs, structural temples and excavated remains. UNESCO describes the Shore Temple as the culmination of structural monuments at the site and notes its Dravida vimana layout along the sea. This source supports the Shore Temple's place in the Pallava architectural sequence; it does not assign every feature of the broader group to this temple."),
        ],
    },
    {
        "temple_id": "meenakshi",
        "missing_topics": ["history", "architecture", "festivals and traditions"],
        "sources_checked": [MADURAI_TEMPLE, MADURAI_FESTIVALS],
        "documents": [
            ("history_architecture_religion", "Meenakshi-Sundareswarar: twin shrines and urban growth", MADURAI_TEMPLE,
             "Madurai District Administration describes Meenakshi and Sundareswarar as the paired deities of the twin-temple complex and says the city developed around it. The district account attributes the complex's growth to successive dynasties and monarchs, and identifies substantial expansion under Thirumalai Nayak (1623–1655 CE). It describes five gateways enclosing the two shrines and highlights the Ayiramkaal Mandapam, or Hall of Thousand Pillars, and stone musical pillars. These are claims in the district tourism account and are retained for human review."),
            ("festivals_traditions", "Madurai temple traditions in the district festival account", MADURAI_FESTIVALS,
             "The Madurai District Administration festival page describes the Chithirai festival, held in April or May, in connection with the marriage of Meenakshi and Sundareswarar and Alagar's journey toward Madurai. The page also lists the cradle festival and Avanimoolam among Madurai's religious events. This is the district's description of local tradition; its mythic narrative is presented as religious tradition rather than independently verifiable historical fact. The page does not provide a current-year schedule."),
        ],
    },
    {
        "temple_id": "kashi_vishwanath",
        "missing_topics": ["architectural history", "festivals", "conservation"],
        "sources_checked": [KASHI_DISTRICT],
        "documents": [
            ("deity_religious_significance", "Kashi Vishvanath: Shiva worship and Jyotirlinga tradition", KASHI_DISTRICT,
             "The Varanasi District Administration identifies Kashi Vishvanath as a Hindu temple dedicated to Shiva on the western bank of the Ganga in Varanasi. It identifies the main deity as Vishvanatha or Vishveshvara and describes the temple as one of the twelve Jyotirlingas. The page explains that the name Kashi is also used for Varanasi. This document covers the district source's religious and location description only; detailed construction history and festival practices remain research gaps."),
        ],
    },
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def main() -> None:
    catalogue = read_json(CATALOGUE_PATH)
    documents = read_json(DOCS_PATH)
    cat_by_id = {row["id"]: row for row in catalogue}
    doc_ids = {row.get("document_id") for row in documents if isinstance(row, dict)}
    baseline_report = DATA / "knowledge_coverage_report_pre_batch_03.json"
    if not baseline_report.exists():
        baseline_report = DATA / "knowledge_coverage_report.json"
    baseline_rows = read_json(baseline_report)["temples"]
    missing_temples = [row["temple_id"] for row in RECORDS if row["temple_id"] not in cat_by_id]
    if missing_temples:
        raise SystemExit(f"Refusing batch: IDs missing from catalogue: {missing_temples}")

    batch_docs = []
    manifest_temples = []
    for record in RECORDS:
        temple = cat_by_id[record["temple_id"]]
        name = temple.get("canonical_name") or (temple.get("names") or [record["temple_id"]])[0]
        temple_docs = []
        for topic, title, source, text in record["documents"]:
            document_id = f"enrich_batch03_{record['temple_id']}_{topic}"
            normalized_text = " ".join(text.split())
            document = {
                "document_id": document_id,
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
                "publication_date": None,
                "retrieval_date": TODAY,
                "collection_timestamp": datetime.now(timezone.utc).isoformat(),
                "content_hash": hashlib.sha256(normalized_text.encode("utf-8")).hexdigest(),
                "verification_status": "source_review_pending",
                "review_status": "pending_human_review",
                "is_paraphrase": True,
                "text": normalized_text,
            }
            temple_docs.append(document)
            if document_id not in doc_ids:
                batch_docs.append(document)
                doc_ids.add(document_id)
        manifest_temples.append({
            "temple_id": record["temple_id"],
            "name": name,
            "state": temple.get("state"),
            "district": temple.get("district"),
            "coverage_before_batch": next((r for r in baseline_rows if r["temple_id"] == record["temple_id"]), {}).get("coverage_class"),
            "current_document_count_before_batch": sum(1 for d in documents if d.get("temple_id") == record["temple_id"]),
            "missing_topics": record["missing_topics"],
            "sources_actually_checked": record["sources_checked"],
            "document_ids": [d["document_id"] for d in temple_docs],
            "enrichment_status": "pending_human_review" if temple_docs else "no_new_document",
            "verification_note": "Source pages were accessed and the limited paraphrased claims were checked against them. Human claim-to-source review remains required; this does not verify the temple as a whole.",
        })

    if batch_docs:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(CATALOGUE_PATH, DATA / f"catalogue.json.batch03_backup_{stamp}")
        shutil.copy2(DOCS_PATH, DATA / "raw" / f"temple_sources.json.batch03_backup_{stamp}")
        documents.extend(batch_docs)
        for doc in batch_docs:
            temple = cat_by_id[doc["temple_id"]]
            temple.setdefault("document_ids", [])
            if doc["document_id"] not in temple["document_ids"]:
                temple["document_ids"].append(doc["document_id"])
            temple.setdefault("sources", [])
            source = {"title": doc["source_title"], "url": doc["source_url"], "publisher": doc["publisher"]}
            if source not in temple["sources"]:
                temple["sources"].append(source)
        write_json(DOCS_PATH, documents)
        write_json(CATALOGUE_PATH, catalogue)

    manifest = {
        "batch_id": BATCH_ID,
        "created_date": TODAY,
        "scope": "10 existing catalogue temples; no new temple records; manually researched source-attributed paraphrases",
        "collection_method": "Manual source page access only; no automated collection; source registry and approval gates unchanged",
        "counts": {
            "temples_in_batch": len(RECORDS),
            "new_documents_prepared": sum(len(row["documents"]) for row in RECORDS),
            "documents_appended_this_run": len(batch_docs),
            "documents_in_batch": sum(len(row["documents"]) for row in RECORDS),
            "pending_human_review": sum(len(row["documents"]) for row in RECORDS),
            "automated_collection_runs": 0,
        },
        "sources_actually_checked": sorted({
            (source["source_title"], source["source_url"], source["publisher"])
            for row in RECORDS for source in row["sources_checked"]
        }),
        "temples": manifest_temples,
        "limitations": [
            "No new material was collected from sources not listed in this batch.",
            "Claims are narrow paraphrases of the cited pages; the pages do not cover every requested topic.",
            "The UNESCO Hampi periodic report is a 2003 condition report; conservation statements are explicitly historical.",
            "Festival narratives are recorded as source-attributed religious tradition, not independent historical fact.",
            "All new documents remain pending human review and are not marked verified.",
        ],
    }
    write_json(MANIFEST_PATH, manifest)
    print(json.dumps({"catalogue_records": len(catalogue), "knowledge_documents": len(documents), "new_documents_added": len(batch_docs), "manifest": str(MANIFEST_PATH), "backups_created": bool(batch_docs)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
