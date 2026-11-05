"""Append a small checkpoint of manually inspected primary-source research.

The pages were opened and their relevant passages read on 2026-11-05. This
script only records source-supported details and deliberately leaves review
status pending. It does not change catalogue records or source permissions.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw" / "temple_sources.json"
PLAN = DATA / "research_plan_all_217.json"
ACCESS_DATE = "2026-11-05"
COLLECTED = datetime.now(timezone.utc).isoformat()

UNESCO_CHOLA = {
    "source_title": "Great Living Chola Temples",
    "source_url": "https://whc.unesco.org/en/list/250/",
    "publisher": "UNESCO World Heritage Centre",
    "source_type": "international_heritage_record",
    "publication_date": None,
}
UNESCO_MAHABODHI = {
    "source_title": "Mahabodhi Temple Complex at Bodh Gaya",
    "source_url": "https://whc.unesco.org/en/list/1056/",
    "publisher": "UNESCO World Heritage Centre",
    "source_type": "international_heritage_record",
    "publication_date": None,
}
UNESCO_MAMALLAPURAM = {
    "source_title": "Group of Monuments at Mahabalipuram",
    "source_url": "https://whc.unesco.org/en/list/249/",
    "publisher": "UNESCO World Heritage Centre",
    "source_type": "international_heritage_record",
    "publication_date": None,
}

DOCUMENTS = [
    {
        "document_id": "all217_research_20261105_brihadisvara_thanjavur_architecture_detail",
        "temple_id": "brihadeeswarar",
        "topic": "architecture_inscriptions",
        "title": "Brihadisvara at Thanjavur: court, sanctum and dance imagery in the UNESCO account",
        **UNESCO_CHOLA,
        "text": "UNESCO's Great Living Chola Temples property description gives a more detailed architectural account of Brihadisvara at Thanjavur. It places the sanctum in the rear half of a rectangular court enclosed by a large colonnaded prakara, with sub-shrines for the ashtadikpalas and an entrance gopura called Rajarajantiruvasal. The page describes a circumambulatory passage around the sanctum and reports that 81 of the 108 karanas are carved on the second bhumi around the garbhagriha. It also identifies mural paintings and an Amman shrine dated approximately to the 13th century. The source gives a vimana height of 59.82 metres; this differs from an approximately 66-metre figure in other corpus material, so the measurement should be checked by a human reviewer before the records are reconciled.",
        "review_status": "pending_human_review",
        "verification_status": "source_review_pending",
    },
    {
        "document_id": "all217_research_20261105_gangaikondacholisvaram_plan_changes",
        "temple_id": "asi_tamil_nadu_9b2980bb768b7c42",
        "topic": "architecture_historical_development",
        "title": "Gangaikondacholisvaram: planned shrines and later additions",
        **UNESCO_CHOLA,
        "text": "UNESCO's account of the Great Living Chola Temples distinguishes the original planned components at Gangaikondacholisvaram from later additions. It identifies the Chandesa and Amman sub-shrines and the Simhakeni, or lion well, as features belonging to Rajendra I's plan; it also lists Thenkailasha, Ganesha and Durga shrines as additions made over time. UNESCO presents those later additions as compatible with the continuing life of a worshipping temple, rather than as evidence that the complex remained unchanged. This is a summary of the UNESCO property description, not an independent inscriptional analysis.",
        "review_status": "pending_human_review",
        "verification_status": "source_review_pending",
    },
    {
        "document_id": "all217_research_20261105_airavatesvara_mandapa_iconography",
        "temple_id": "asi_tamil_nadu_64f350d8e3dc3e9c",
        "topic": "architecture_inscriptions_iconography",
        "title": "Airavatesvara: chariot-form mandapa and Nayanmar friezes",
        **UNESCO_CHOLA,
        "text": "UNESCO describes Airavatesvara at Darasuram as a complex with a sanctum that has no circumambulatory path and with axial mandapas. Its front mandapa is identified in inscriptions as Rajagambhiran tirumandapam and is conceived as a chariot with wheels. UNESCO notes the ornate pillars and sculpture-dominated elevations, and singles out labelled miniature friezes depicting episodes associated with the 63 Nayanmars, or Saiva saints. The description also records a separate Deivanayaki Amman shrine built slightly later than the main temple. These details are specific to the Darasuram component of the World Heritage property.",
        "review_status": "pending_human_review",
        "verification_status": "source_review_pending",
    },
    {
        "document_id": "all217_research_20261105_mahabodhi_conservation_history",
        "temple_id": "whc_b64d0b1bb2989639c1f1",
        "topic": "heritage_conservation_management",
        "title": "Mahabodhi: documented restoration history and management framework",
        **UNESCO_MAHABODHI,
        "text": "The UNESCO property account describes the Mahabodhi complex as having components from different periods. It records the main temple as dating broadly to the 5th–6th centuries CE, followed by repairs and renovations, a long period of abandonment described as spanning the 13th–18th centuries, extensive restoration in the 19th century and further work in the second half of the 20th century. UNESCO identifies the State Government of Bihar and the Bodhgaya Temple Management Committee as responsible for management under the Bodh Gaya Temple Act of 1949, and says conservation and restoration work is undertaken with expert guidance from the Archaeological Survey of India. This is the dated historical account presented by the source; it is not a report of present-day condition.",
        "review_status": "pending_human_review",
        "verification_status": "source_review_pending",
    },
    {
        "document_id": "all217_research_20261105_shore_temple_pallava_development",
        "temple_id": "shore",
        "topic": "architecture_historical_development_heritage",
        "title": "Shore Temple in the Pallava sequence of rock-cut and structural monuments",
        **UNESCO_MAMALLAPURAM,
        "text": "UNESCO places the Shore Temple within the wider Pallava monument group at Mahabalipuram and describes it as the culmination of the site's structural temple building. The same account distinguishes rock-cut cave mandapas, monolithic rathas carved from large boulders, open-air reliefs and structural temples, presenting these as different stages and forms of Pallava architectural work rather than as parts of the Shore Temple alone. UNESCO also records excavated remains around the Shore Temple, including a stepped structure, miniature shrine, Bhuvaraha image, reclining Vishnu image and a well carved from bedrock, which it associates with the reign of Narasimhavarman Rajasimha (638–660 CE). These are site-group findings and should not be confused with features inside the Shore Temple itself.",
        "review_status": "pending_human_review",
        "verification_status": "source_review_pending",
    },
]


def main() -> None:
    docs = json.loads(RAW.read_text(encoding="utf-8"))
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    catalogue = json.loads((DATA / "catalogue.json").read_text(encoding="utf-8"))
    temple_by_id = {t["id"]: t for t in catalogue}
    existing = {d.get("document_id") for d in docs}
    plan_by_id = {t["temple_id"]: t for t in plan["temples"]}
    for doc in DOCUMENTS:
        if doc["document_id"] in existing:
            raise ValueError(f"Refusing to overwrite existing document {doc['document_id']}")
        temple = temple_by_id.get(doc["temple_id"])
        if not temple:
            raise ValueError(f"Unknown catalogue temple ID {doc['temple_id']}")
        doc.update({
            "temple_name": temple.get("canonical_name") or (temple.get("names") or [doc["temple_id"]])[0],
            "state": temple.get("state"),
            "district": temple.get("district"),
            "language": "en",
            "retrieval_date": ACCESS_DATE,
            "collection_timestamp": COLLECTED,
            "content_hash": hashlib.sha256(" ".join(doc["text"].split()).encode("utf-8")).hexdigest(),
            "is_paraphrase": True,
        })
        docs.append(doc)
        existing.add(doc["document_id"])
    source_catalog = [
        ("UNESCO World Heritage Centre", "https://whc.unesco.org/en/list/1570/", "international_heritage_record", ["asi_telangana_f3a7458053e48f24"], ["historical_background", "architecture", "religious_cultural_significance", "heritage_conservation"]),
        ("Great Living Chola Temples", UNESCO_CHOLA["source_url"], "international_heritage_record", ["brihadeeswarar", "asi_tamil_nadu_9b2980bb768b7c42", "asi_tamil_nadu_64f350d8e3dc3e9c"], ["historical_background", "architecture", "religious_cultural_significance", "heritage_conservation", "inscriptions_historical_evidence"]),
        ("Group of Monuments at Pattadakal", "https://whc.unesco.org/en/list/239", "international_heritage_record", ["asi_karnataka_7c32bc783d1664dc"], ["historical_background", "architecture"]),
        ("Group of Monuments at Hampi", "https://whc.unesco.org/en/list/241/", "international_heritage_record", ["whc_0601b84399076df5f6eb", "whc_ffb69144fee941fb01a9"], ["historical_background", "architecture", "religious_cultural_significance", "festivals_traditions", "heritage_conservation"]),
        (UNESCO_MAMALLAPURAM["source_title"], UNESCO_MAMALLAPURAM["source_url"], "international_heritage_record", ["shore"], ["historical_background", "architecture", "religious_cultural_significance", "heritage_conservation"]),
        ("Khajuraho Group of Monuments", "https://whc.unesco.org/en/list/240/", "international_heritage_record", ["whc_798b3d431ca45563a0f8"], ["historical_background", "architecture", "religious_cultural_significance", "heritage_conservation"]),
        (UNESCO_MAHABODHI["source_title"], UNESCO_MAHABODHI["source_url"], "international_heritage_record", ["whc_b64d0b1bb2989639c1f1"], ["historical_background", "architecture", "religious_cultural_significance", "heritage_conservation", "visitor_information"]),
    ]
    source_checks = [{
        "source_title": title, "source_url": url, "publisher": "UNESCO World Heritage Centre",
        "source_type": source_type, "publication_date": None, "accessed_date": ACCESS_DATE,
        "inspection_method": "Opened and reviewed page text in browser search/open result; no bulk download or crawler used.",
        "linked_temple_ids": tids, "categories_with_relevant_source_content": categories,
    } for title, url, source_type, tids, categories in source_catalog]
    source_checks.append({"source_title": "Epigraphy", "source_url": "https://www.tnarch.gov.in/epigraphy", "publisher": "Tamil Nadu Department of Archaeology", "source_type": "official_archaeology_department_page", "publication_date": None, "accessed_date": ACCESS_DATE, "inspection_method": "Opened page; reviewed agency description of epigraphic work and inscription media. General method only, not temple-specific evidence.", "linked_temple_ids": [], "categories_with_relevant_source_content": ["inscriptions_historical_evidence"]})
    for temple_id, row in plan_by_id.items():
        matches = [s for s in source_checks if temple_id in s["linked_temple_ids"]]
        if not matches:
            continue
        row["research_status"] = "primary_source_inspected_partial_categories"
        row["source_checks"] = matches
        covered = {category for source in matches for category in source["categories_with_relevant_source_content"]}
        for category, detail in row["categories"].items():
            if category in covered:
                detail["research_status"] = "source_inspected_evidence_or_context_found"
            elif detail["coverage_status"] == "Missing":
                detail["research_status"] = "source_reviewed_no_supporting_content_on_checked_pages"
        row["research_notes"] = "External source page(s) were inspected on 2026-11-05. This is partial category research only; page-level evidence remains pending human review and unresearched categories stay open. Group-level claims are explicitly labelled as such in documents."
    plan["source_checks_this_operation"] = source_checks
    plan["inaccessible_or_unmapped_source_attempts"] = [{
        "source_title": "Arulmigu Naganathaswamy temple", "source_url": "https://www.tnarch.gov.in/node/430",
        "publisher": "Tamil Nadu Department of Archaeology", "status": "direct_page_open_timed_out_and_no_catalogue_record_matched",
        "search_result_text_used_as_evidence": False,
    }]
    plan["temples_with_external_source_pages_inspected_this_operation"] = sum(bool(r.get("source_checks")) for r in plan["temples"])
    plan["temples_not_yet_researched_this_operation"] = len(plan["temples"]) - plan["temples_with_external_source_pages_inspected_this_operation"]
    plan["research_status_note"] = "This is a partial checkpoint. Only temples directly linked in source_checks have inspected source pages; the remaining catalogue entries are not researched in this operation."
    RAW.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"new_documents": len(DOCUMENTS), "source_pages_inspected": len(source_checks), "temples_with_pages_inspected": plan["temples_with_external_source_pages_inspected_this_operation"], "still_unresearched": plan["temples_not_yet_researched_this_operation"], "document_total": len(docs)}, indent=2))


if __name__ == "__main__":
    main()
