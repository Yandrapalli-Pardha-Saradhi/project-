"""Append a second manually inspected UNESCO research checkpoint."""
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

SOURCES = {
    "hoysala_2023": {
        "source_title": "Decision 45 COM 8B.38 — Sacred Ensembles of the Hoysalas",
        "source_url": "https://whc.unesco.org/en/decisions/8419",
        "publisher": "UNESCO World Heritage Committee",
        "source_type": "international_heritage_committee_decision",
        "publication_date": "2023",
    },
    "hoysala_2025": {
        "source_title": "Decision 47 COM 7B.73 — Sacred Ensembles of the Hoysalas",
        "source_url": "https://whc.unesco.org/en/decisions/8797",
        "publisher": "UNESCO World Heritage Committee",
        "source_type": "international_heritage_committee_decision",
        "publication_date": "2025",
    },
}

DOCS = [
    ("asi_karnataka_d5d33227e0a3a92f", "hoysala_2023", "religious_use", "Hoysalesvara at Halebidu: worship status recorded in UNESCO's 2023 nomination decision", "UNESCO's 2023 decision for the Sacred Ensembles of the Hoysalas describes worship at Hoysalesvara Temple, Halebidu, as long discontinued. It says only symbolic worship is permitted and that rituals and festivals are not allowed. This is a statement in the nomination-era UNESCO record, not a live access notice; present rules should be checked with the responsible authorities. The same decision identifies Hoysalesvara as one of three components of the inscribed serial property, alongside Belur and Somanathapura."),
    ("asi_karnataka_f29968094d7b92b1", "hoysala_2023", "religious_use", "Keshava at Somanathapura: UNESCO record of non-worshipping use", "UNESCO's 2023 decision identifies Keshava Temple at Somanathapura as one of the three component monuments of the Sacred Ensembles of the Hoysalas and describes it as a non-worshipping temple. The statement concerns the temple's use as recorded for the World Heritage nomination; it does not establish current visitor hours, admission rules or access arrangements."),
    ("asi_karnataka_d5d33227e0a3a92f", "hoysala_2025", "heritage_conservation_air_pollution", "Halebidu within the 2025 UNESCO conservation decision for the Hoysala ensembles", "In its 2025 decision on the Sacred Ensembles of the Hoysalas, the World Heritage Committee notes progress in community involvement and conservation around the Belur component and records the State Party's commitment to monitor air-pollution impacts on sculptures across the serial property's components. The decision encourages mitigation based on monitoring outcomes and requests an updated state-of-conservation report by 1 December 2026. These are group-level management observations and a dated committee request, not a current condition assessment specific to every Hoysalesvara sculpture."),
    ("asi_karnataka_f29968094d7b92b1", "hoysala_2025", "heritage_conservation_air_pollution", "Somanathapura within the 2025 UNESCO conservation decision for the Hoysala ensembles", "The 2025 UNESCO World Heritage Committee decision treats Keshava Temple at Somanathapura as a component of the Sacred Ensembles of the Hoysalas and encourages monitoring and mitigation of air-pollution impacts on the serial property's sculptures. It also records progress at Belur and asks the State Party for an updated conservation report by 1 December 2026. The Belur-specific progress statements should not be transferred to Somanathapura; only the serial-property monitoring request applies here."),
]


def main() -> None:
    docs = json.loads(RAW.read_text(encoding="utf-8"))
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    catalogue = json.loads((DATA / "catalogue.json").read_text(encoding="utf-8"))
    by_id = {t["id"]: t for t in catalogue}
    existing = {d.get("document_id") for d in docs}
    for temple_id, source_key, topic, title, text in DOCS:
        document_id = f"all217_research_20261105_{temple_id}_{topic}"
        if document_id in existing:
            raise ValueError(f"Refusing to overwrite existing document {document_id}")
        temple = by_id.get(temple_id)
        if not temple:
            raise ValueError(f"Unknown catalogue temple ID {temple_id}")
        source = SOURCES[source_key]
        docs.append({
            "document_id": document_id,
            "temple_id": temple_id,
            "temple_name": temple.get("canonical_name") or (temple.get("names") or [temple_id])[0],
            "state": temple.get("state"),
            "district": temple.get("district"),
            "topic": topic,
            "title": title,
            **source,
            "language": "en",
            "retrieval_date": ACCESS_DATE,
            "collection_timestamp": COLLECTED,
            "content_hash": hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest(),
            "verification_status": "source_review_pending",
            "review_status": "pending_human_review",
            "is_paraphrase": True,
            "text": text,
        })
        existing.add(document_id)
    checks = [
        {**source, "accessed_date": ACCESS_DATE, "inspection_method": "Opened and read decision text; no automated collection.", "linked_temple_ids": tids, "categories_with_relevant_source_content": categories}
        for source, tids, categories in [
            (SOURCES["hoysala_2023"], ["asi_karnataka_d5d33227e0a3a92f", "asi_karnataka_f29968094d7b92b1"], ["historical_background", "architecture", "religious_cultural_significance", "festivals_traditions", "heritage_conservation"]),
            (SOURCES["hoysala_2025"], ["asi_karnataka_d5d33227e0a3a92f", "asi_karnataka_f29968094d7b92b1"], ["heritage_conservation"]),
            ({"source_title": "Sun Temple, Konârak", "source_url": "https://whc.unesco.org/en/list/246/", "publisher": "UNESCO World Heritage Centre", "source_type": "international_heritage_record", "publication_date": None}, ["konark"], ["historical_background", "architecture", "religious_cultural_significance", "festivals_traditions", "heritage_conservation"]),
        ]
    ]
    plan_by_id = {row["temple_id"]: row for row in plan["temples"]}
    for check in checks:
        if not any(old.get("source_url") == check["source_url"] for old in plan.setdefault("source_checks_this_operation", [])):
            plan["source_checks_this_operation"].append(check)
        for tid in check["linked_temple_ids"]:
            row = plan_by_id[tid]
            row.setdefault("source_checks", []).append(check)
            row["research_status"] = "primary_source_inspected_partial_categories"
            covered = set(check["categories_with_relevant_source_content"])
            for category in covered:
                if category in row.get("categories", {}):
                    row["categories"][category]["research_status"] = "source_inspected_evidence_or_context_found"
            if tid == "konark":
                row["research_notes"] = "UNESCO's live property page was opened and read on 2026-11-05. Existing Batch 4 documents already capture most of the facts inspected; no duplicate knowledge documents were added for this temple in the current checkpoint."
            else:
                row["research_notes"] = "UNESCO committee decision pages from 2023 and 2025 were opened and read on 2026-11-05. New use/conservation notes are narrowly scoped and pending human review; remaining source and topic gaps are open."
    plan["temples_with_external_source_pages_inspected_this_operation"] = sum(bool(r.get("source_checks")) for r in plan["temples"])
    plan["temples_not_yet_researched_this_operation"] = len(plan["temples"]) - plan["temples_with_external_source_pages_inspected_this_operation"]
    plan["new_documents_added_this_operation"] = sum(str(d.get("document_id", "")).startswith("all217_research_20261105_") for d in docs)
    plan["temples_with_new_documents_pending_review"] = len({d.get("temple_id") for d in docs if str(d.get("document_id", "")).startswith("all217_research_20261105_")})
    plan["current_knowledge_document_count"] = len(docs)
    plan["last_updated_utc"] = datetime.now(timezone.utc).isoformat()
    plan["research_status_note"] = "Partial source-research checkpoints only. Every unlinked catalogue record remains unresearched in this operation; source-linked entries still have category gaps."
    RAW.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"new_documents": len(DOCS), "current_documents": len(docs), "temples_with_source_pages_inspected": plan["temples_with_external_source_pages_inspected_this_operation"], "still_not_researched": plan["temples_not_yet_researched_this_operation"], "source_page_count": len(plan["source_checks_this_operation"])}, indent=2))


if __name__ == "__main__":
    main()
