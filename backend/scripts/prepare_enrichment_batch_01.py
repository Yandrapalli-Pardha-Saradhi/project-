"""Idempotently add the manually reviewed, source-attributed first enrichment batch.

This is a small editorial seed, not a collector. It performs no network access and
does not change source-registry approval gates. Every new document remains pending
human review until an operator verifies the paraphrase against its cited source.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE_PATH = ROOT / "data" / "catalogue.json"
DOCUMENTS_PATH = ROOT / "data" / "raw" / "temple_sources.json"
MANIFEST_PATH = ROOT / "data" / "enrichment_manifest_batch_01.json"
AS_OF = date(2026, 11, 5).isoformat()

# First 20 inventory-only candidates, balanced across Tamil Nadu and Karnataka.
# The ordering deliberately favors places for which an authoritative source was
# checked. Remaining candidates stay visible in the manifest as research work.
BATCH = [
    ("asi_tamil_nadu_228792b71860b713", "Tamil Nadu"),
    ("asi_tamil_nadu_b8864915b92941b5", "Tamil Nadu"),
    ("asi_tamil_nadu_8efa92f0aa42a214", "Tamil Nadu"),
    ("asi_tamil_nadu_476eb8cc97fb84ef", "Tamil Nadu"),
    ("asi_tamil_nadu_94ef770652db64a5", "Tamil Nadu"),
    ("asi_tamil_nadu_c4c0740aa244e2f1", "Tamil Nadu"),
    ("asi_tamil_nadu_dfe60f19c80a4e44", "Tamil Nadu"),
    ("asi_tamil_nadu_4c1f14f2232e8d73", "Tamil Nadu"),
    ("asi_tamil_nadu_f4f02026c173d091", "Tamil Nadu"),
    ("asi_tamil_nadu_9ff95b5f3937c27a", "Tamil Nadu"),
    ("asi_karnataka_39c8b5453cc604ec", "Karnataka"),
    ("asi_karnataka_df9d7ed1a005d4a6", "Karnataka"),
    ("asi_karnataka_20e758c06d541bd9", "Karnataka"),
    ("asi_karnataka_e7e3292346518668", "Karnataka"),
    ("asi_karnataka_1544f0a56a8c103b", "Karnataka"),
    ("asi_karnataka_43d31d5b7b909f6e", "Karnataka"),
    ("asi_karnataka_4e9044ce27267cfb", "Karnataka"),
    ("asi_karnataka_80d2910c86f3032b", "Karnataka"),
    ("asi_karnataka_2494fc98f5e2568d", "Karnataka"),
    ("asi_karnataka_a0dee297d7802db0", "Karnataka"),
]

# Conservative, source-grounded summaries. These are editorial paraphrases of
# the named pages/publications, not claims that the whole temple record is verified.
ENRICHMENTS = {
    "asi_tamil_nadu_228792b71860b713": {
        "topic": "history_architecture",
        "title": "Venkataramana Temple, Gingee — Viluppuram District Administration",
        "url": "https://viluppuram.nic.in/tourism/place-of-interest/",
        "publisher": "Viluppuram District Administration, Government of Tamil Nadu",
        "type": "official_government_page_paraphrase",
        "text": "The Viluppuram District Administration describes Gingee's Venkataramana Temple as a Nayaka-period foundation associated with Muthialu Nayaka and dates its construction to 1540–1550. The account notes gopuras and mandapas, sculpted panels depicting episodes from the epics, and Tamil inscriptions. It also records damage and decline following the French occupation after 1761. These details are reported by the district tourism page and remain pending editorial review against the source.",
    },
    "asi_tamil_nadu_94ef770652db64a5": {
        "topic": "history_architecture",
        "title": "Mandagapattu — Viluppuram District Administration",
        "url": "https://viluppuram.nic.in/tourism/place-of-interest/",
        "publisher": "Viluppuram District Administration, Government of Tamil Nadu",
        "type": "official_government_page_paraphrase",
        "text": "The Viluppuram District Administration identifies the Mandagapattu rock-cut shrine as a Pallava cave temple associated with Mahendravarman I. Its tourism account gives an early seventh-century date range and locates it near Gingee. The page's chronology is reproduced only as a source-attributed report here; the exact date and interpretation need specialist review. No deity or architectural details beyond those explicitly stated by the source are asserted in this document.",
    },
    "asi_tamil_nadu_c4c0740aa244e2f1": {
        "topic": "architecture_conservation",
        "title": "Indian Archaeology 1975–76: A Review — Panamalai report",
        "url": "https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%201975-76%20A%20Review.pdf",
        "publisher": "Archaeological Survey of India, Indian Archaeology: A Review",
        "type": "official_archaeological_report_paraphrase",
        "text": "The Archaeological Survey of India's 1975–76 review reports archaeological work at the Talagirisvara temple at Panamalai, including the removal of later brick accretions that exposed Pallava inscriptions on the temple plinth and vimana. This is a narrowly scoped report of an archaeological observation, not a complete history or conservation assessment. The publication's exact passage and terminology should be checked during human review before this note is treated as settled.",
    },
    "asi_tamil_nadu_4c1f14f2232e8d73": {
        "topic": "history_architecture_culture",
        "title": "Kailasanatha Temple, Kanchipuram — Incredible India",
        "url": "https://www.incredibleindia.gov.in/en/tamil-nadu/kanchipuram/kailasanatha-temple",
        "publisher": "Ministry of Tourism, Government of India",
        "type": "official_tourism_page_paraphrase",
        "text": "The Government of India's Incredible India page dates Kanchipuram's Kailasanatha Temple to around 700 CE and associates its construction with Pallava ruler Narasimhavarman II (Rajasimha), with additions attributed to Mahendravarman III. It describes a complex combining rock-cut and structural stone work, a Shiva lingam, subsidiary shrines, a vimana and mandapa with carved reliefs, inscriptions and murals. The page also identifies Maha Shivratri as a significant observance. These are source-reported claims pending human review.",
    },
    "asi_tamil_nadu_f4f02026c173d091": {
        "topic": "history_architecture",
        "title": "Archaeological Remains at Srinivasanallur — IGNCA digital library",
        "url": "https://ignca.gov.in/Asi_data/37526.pdf",
        "publisher": "Indira Gandhi National Centre for the Arts, digitized archaeological publication",
        "type": "institutional_archaeological_publication_paraphrase",
        "text": "The digitized archaeological publication hosted by the Indira Gandhi National Centre for the Arts discusses the Korangunatha temple at Srinivasanallur and associates it with the reign of Parantaka I (907–955 CE). Its description notes a square vimana, a mandapa, sculptural work and miniature panels; it also remarks on surviving brick fabric in the superstructure. This note is attributed to that publication and requires a page-level editorial check before its architectural and chronological details are treated as verified.",
    },
    "asi_karnataka_80d2910c86f3032b": {
        "topic": "history_architecture_culture",
        "title": "Sri Vidyashankara Temple — Sringeri Sharada Peetham",
        "url": "https://www.srisharadapeetham.org/temples/sri-vidyashankara",
        "publisher": "Sri Sharada Peetham, Sringeri",
        "type": "temple_authority_page_paraphrase",
        "text": "The Sringeri Sharada Peetham's temple account dates Vidyashankara Temple to 1338 CE and describes its stone construction and combination of Hoysala and Dravidian features. It highlights twelve zodiac-associated pillars and records the Vidyatirtha Rathotsava during Kartika as a seven-day observance. The temple authority also notes the Archaeological Survey of India's role in its care. These statements reflect the cited institution's account and remain pending independent editorial review.",
    },
    "asi_karnataka_1544f0a56a8c103b": {
        "topic": "history_heritage",
        "title": "Nandi Hills — Karnataka Tourism",
        "url": "https://karnatakatourism.org/en/experiences/nandi-hills-bengaluru/",
        "publisher": "Karnataka Tourism, Government of Karnataka",
        "type": "official_tourism_page_paraphrase",
        "text": "Karnataka Tourism describes the Bhoga Nandeeshwara Temple complex at Nandi as an ancient temple complex and gives a ninth-century date in its Nandi Hills visitor overview. This source supports only a concise heritage note; it does not establish detailed construction phases, individual architectural elements, or festival practices for this record. The date and scope are kept attributed to the tourism page and pending review.",
    },
    "asi_karnataka_4e9044ce27267cfb": {
        "topic": "history_heritage",
        "title": "Hoysala temples of Belavadi — UNESCO Tentative List dossier",
        "url": "https://whc.unesco.org/document/198086",
        "publisher": "UNESCO World Heritage Centre, tentative-list nomination dossier",
        "type": "institutional_nomination_dossier_paraphrase",
        "text": "The UNESCO-hosted Hoysala temples nomination dossier inventories the Veera Narayana temple at Belavadi, records 1206 CE as its establishment date, and describes it as a living temple under Archaeological Survey of India ownership. The dossier identifies Veera Narayana as the principal shrine and mentions Venu Gopala and Yoga Narasimha subsidiary shrines. Belavadi is documented in a nomination dossier; this source does not mean this individual temple is independently inscribed on UNESCO's World Heritage List. The dossier's claims remain pending review.",
    },
    "asi_karnataka_a0dee297d7802db0": {
        "topic": "architecture_history_religion",
        "title": "Badami — Incredible India",
        "url": "https://www.incredibleindia.gov.in/en/karnataka/badami",
        "publisher": "Ministry of Tourism, Government of India",
        "type": "official_tourism_page_paraphrase",
        "text": "The Government of India's Incredible India page describes Badami's cave-temple group as four rock-cut sanctuaries with a hall, pillared veranda and shrine area. Its account identifies Shaiva imagery in Cave 1, Vaishnava imagery in Caves 2 and 3, and a Jain cave (Cave 4), and places the group in the early Chalukya period. This note is limited to the page's broad description; individual dates, iconographic identifications and conservation details require human source review.",
    },
    "asi_karnataka_2494fc98f5e2568d": {
        "topic": "architecture_heritage",
        "title": "Aihole — Incredible India",
        "url": "https://www.incredibleindia.gov.in/en/karnataka/badami/aihole",
        "publisher": "Ministry of Tourism, Government of India",
        "type": "official_tourism_page_paraphrase",
        "text": "The Government of India's Aihole page describes the Durga Temple's distinctive apsidal plan, raised platform and gallery surrounding its sanctum, and notes Archaeological Survey of India conservation. The page presents Aihole as an important early Chalukya temple center. This document records only those broad source-supported points; it does not infer the temple's dedication from its commonly used name. The source and its terminology remain pending editorial review.",
    },
}

SOURCE_CANDIDATES = {
    "asi_tamil_nadu_228792b71860b713": ["https://viluppuram.nic.in/tourism/place-of-interest/"],
    "asi_tamil_nadu_b8864915b92941b5": ["https://viluppuram.nic.in/tourism/place-of-interest/"],
    "asi_tamil_nadu_8efa92f0aa42a214": ["https://viluppuram.nic.in/tourism/place-of-interest/", "https://asichennai.gov.in/monuments_full_list.html"],
    "asi_tamil_nadu_476eb8cc97fb84ef": ["https://viluppuram.nic.in/tourism/place-of-interest/", "https://asichennai.gov.in/monuments_full_list.html"],
    "asi_tamil_nadu_94ef770652db64a5": ["https://viluppuram.nic.in/tourism/place-of-interest/"],
    "asi_tamil_nadu_c4c0740aa244e2f1": ["https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%201975-76%20A%20Review.pdf", "https://asichennai.gov.in/monuments_full_list.html"],
    "asi_tamil_nadu_dfe60f19c80a4e44": ["https://asichennai.gov.in/monuments_full_list.html"],
    "asi_tamil_nadu_391fcec2d80aafc7": ["https://asichennai.gov.in/monuments_full_list.html"],
    "asi_tamil_nadu_e61d14dae331b5c6": ["https://asichennai.gov.in/monuments_full_list.html"],
    "asi_tamil_nadu_9ff95b5f3937c27a": ["https://asichennai.gov.in/monuments_full_list.html"],
    "asi_karnataka_39c8b5453cc604ec": ["https://asi.nic.in/pdf/CPM_List.pdf"],
    "asi_karnataka_df9d7ed1a005d4a6": ["https://asi.nic.in/pdf/CPM_List.pdf"],
    "asi_karnataka_20e758c06d541bd9": ["https://asi.nic.in/pdf/CPM_List.pdf"],
    "asi_karnataka_e7e3292346518668": ["https://asi.nic.in/pdf/CPM_List.pdf"],
    "asi_karnataka_1544f0a56a8c103b": ["https://karnatakatourism.org/en/experiences/nandi-hills-bengaluru/"],
    "asi_karnataka_43d31d5b7b909f6e": ["https://asi.nic.in/pdf/CPM_List.pdf"],
    "asi_karnataka_4e9044ce27267cfb": ["https://whc.unesco.org/document/198086"],
    "asi_karnataka_80d2910c86f3032b": ["https://www.srisharadapeetham.org/temples/sri-vidyashankara"],
    "asi_karnataka_4a69d324a639a65c": ["https://asi.nic.in/pdf/CPM_List.pdf"],
    "asi_karnataka_3853d41ca24309c8": ["https://asi.nic.in/pdf/CPM_List.pdf"],
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    catalogue = read_json(CATALOGUE_PATH)
    documents = read_json(DOCUMENTS_PATH)
    by_id = {temple["id"]: temple for temple in catalogue}
    docs_for = {}
    for doc in documents:
        docs_for.setdefault(doc.get("temple_id"), []).append(doc)

    missing_ids = [temple_id for temple_id, _ in BATCH if temple_id not in by_id]
    if missing_ids:
        raise SystemExit(f"Catalogue is missing batch IDs: {missing_ids}")
    for temple_id, state in BATCH:
        existing = docs_for.get(temple_id, [])
        expected_enrichment_id = f"enrich_20261105_{temple_id}"
        unexpected = [
            doc for doc in existing
            if doc.get("topic") != "asi_inventory_listing"
            and doc.get("document_id") != expected_enrichment_id
        ]
        if not existing or unexpected:
            raise SystemExit(f"Batch member is no longer inventory-only: {temple_id}")
        if by_id[temple_id].get("state") != state:
            raise SystemExit(f"Unexpected state for {temple_id}: {by_id[temple_id].get('state')}")

    known_doc_ids = {doc.get("document_id") for doc in documents}
    manifest_items = []
    for temple_id, state in BATCH:
        temple = by_id[temple_id]
        name = temple.get("canonical_name") or (temple.get("names") or [temple_id])[0]
        addition = ENRICHMENTS.get(temple_id)
        baseline_docs = [
            doc for doc in docs_for[temple_id]
            if doc.get("document_id") != f"enrich_20261105_{temple_id}"
        ]
        manifest_items.append({
            "temple_id": temple_id,
            "name": name,
            "state": state,
            "district": temple.get("district"),
            "current_document_coverage": sorted({doc.get("topic", "unknown") for doc in baseline_docs}),
            "missing_topics": ["history", "architecture", "deity_or_tradition", "festivals", "heritage_status", "conservation"],
            "candidate_authoritative_sources": SOURCE_CANDIDATES.get(temple_id, []),
            "enrichment_status": "draft_pending_human_review" if addition else "source_gap_pending_research",
            "document_id_added": f"enrich_20261105_{temple_id}" if addition else None,
            "review_notes": (
                "Source checked for limited claims; paraphrase and claim-to-source mapping still require human review. Not temple-wide verification."
                if addition else
                "No substantive source checked for this record in batch 1; inventory listing supports identification/location only. Do not infer missing topics."
            ),
        })

    added = []
    for temple_id, payload in ENRICHMENTS.items():
        document_id = f"enrich_20261105_{temple_id}"
        if document_id in known_doc_ids:
            continue
        temple = by_id[temple_id]
        doc = {
            "document_id": document_id,
            "temple_id": temple_id,
            "temple_name": temple.get("canonical_name") or temple["names"][0],
            "state": temple.get("state"),
            "district": temple.get("district"),
            "source_title": payload["title"],
            "source_url": payload["url"],
            "publisher": payload["publisher"],
            "source_type": payload["type"],
            "topic": payload["topic"],
            "language": "en",
            "publication_date": None,
            "retrieval_date": AS_OF,
            "collection_timestamp": None,
            "verification_status": "source_review_pending",
            "review_status": "pending_human_source_review",
            "is_paraphrase": True,
            "text": payload["text"],
        }
        documents.append(doc)
        known_doc_ids.add(document_id)
        added.append(doc)
        # Preserve existing details; append provenance and document linkage only.
        source_entry = {"title": payload["title"], "url": payload["url"], "publisher": payload["publisher"]}
        sources = temple.setdefault("sources", [])
        if not any(item.get("url") == payload["url"] for item in sources if isinstance(item, dict)):
            sources.append(source_entry)
        linked = temple.setdefault("document_ids", [])
        if document_id not in linked:
            linked.append(document_id)

    # Validate expected one-to-one links before writing any product.
    assert len(BATCH) == 20 and sum(state == "Tamil Nadu" for _, state in BATCH) == 10
    assert sum(state == "Karnataka" for _, state in BATCH) == 10
    if len({item["temple_id"] for item in manifest_items}) != len(BATCH):
        raise SystemExit("Duplicate temple in manifest batch")

    CATALOGUE_PATH.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    DOCUMENTS_PATH.write_text(json.dumps(documents, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "batch_id": "2026-11-05-batch-01",
        "created_date": AS_OF,
        "scope": "20 existing inventory-only catalogue records; no new temple records",
        "source_collection": "Manual source checks only; no automated collection run. Source approval gates unchanged.",
        "counts": {"temples_in_batch": len(BATCH), "draft_documents_added": len(added), "pending_research": len(BATCH) - len(added)},
        "temples": manifest_items,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"catalogue_records": len(catalogue), "documents_before": len(documents) - len(added), "documents_after": len(documents), "batch_temples": len(BATCH), "new_documents": len(added), "manifest": str(MANIFEST_PATH)}, indent=2))


if __name__ == "__main__":
    main()
