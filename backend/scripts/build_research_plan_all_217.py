"""Create a per-temple source-research queue from the current audit artifacts.

This does not collect web pages or claim that temples are researched. It
preserves the audit's evidence leads and records source-registry gates.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CATEGORIES = {
    "historical_background": ["history", "origin", "construction", "dynasty", "ruler", "timeline"],
    "architecture": ["architecture", "plan", "sanctum", "mandapa", "gopuram", "vimana", "sculpture"],
    "religious_cultural_significance": ["deity", "worship", "tradition", "pilgrimage", "legend", "cultural significance"],
    "festivals_traditions": ["festival", "ritual", "procession", "annual celebration", "ceremony"],
    "inscriptions_historical_evidence": ["inscription", "epigraphy", "donation record", "grant", "script", "archaeological evidence"],
    "heritage_conservation": ["ASI protection", "heritage status", "UNESCO status", "conservation", "restoration", "preservation"],
    "visitor_information": ["official visiting hours", "entry fee", "accessibility", "visitor guidance", "access information"],
}


def main() -> None:
    catalogue = json.loads((DATA / "catalogue.json").read_text(encoding="utf-8"))
    docs = json.loads((DATA / "raw" / "temple_sources.json").read_text(encoding="utf-8"))
    coverage = json.loads((DATA / "knowledge_coverage_report_final.json").read_text(encoding="utf-8"))
    registry = json.loads((DATA / "source_registry.json").read_text(encoding="utf-8"))
    coverage_by_id = {row["temple_id"]: row for row in coverage["temples"]}
    docs_by_id: dict[str, list[dict]] = {}
    for doc in docs:
        docs_by_id.setdefault(doc.get("temple_id", ""), []).append(doc)
    sources = registry.get("sources", [])
    rows = []
    for temple in catalogue:
        tid = temple["id"]
        audit = coverage_by_id.get(tid, {})
        cats = audit.get("categories", {})
        category_rows = {}
        for name, query_terms in CATEGORIES.items():
            audit_name = "historical_background" if name == "inscriptions_historical_evidence" else name
            evidence = cats.get(audit_name, {})
            category_rows[name] = {
                "coverage_status": evidence.get("status", "Missing") if name != "inscriptions_historical_evidence" else "Not separately scored; inspect source documents",
                "existing_document_ids": evidence.get("document_ids", []) if name != "inscriptions_historical_evidence" else [d.get("document_id") for d in docs_by_id.get(tid, [])],
                "existing_source_urls": evidence.get("source_urls", []) if name != "inscriptions_historical_evidence" else list(dict.fromkeys(d.get("source_url") for d in docs_by_id.get(tid, []) if d.get("source_url"))),
                "research_queries_required": [
                    f'"{temple.get("canonical_name", (temple.get("names") or [tid])[0])}" {temple.get("district", "")} {term}'.strip()
                    for term in query_terms
                ],
                "research_status": "pending_external_source_inspection",
            }
        source_candidates = [
            {"source_id": s.get("id"), "name": s.get("name"), "base_url": s.get("base_url"),
             "enabled": s.get("enabled"), "permitted_collection_method": s.get("permitted_collection_method"),
             "terms_review_status": s.get("terms_review_status"), "collection_gate": "Do not automate; inspect manually only where permitted."}
            for s in sources
        ]
        rows.append({
            "temple_id": tid,
            "canonical_name": temple.get("canonical_name") or (temple.get("names") or [tid])[0],
            "alternate_names": temple.get("alternate_names", []),
            "state": temple.get("state"),
            "district": temple.get("district"),
            "existing_document_count": len(docs_by_id.get(tid, [])),
            "existing_coverage_class_heuristic": audit.get("coverage_class_heuristic"),
            "existing_coverage_by_category": {k: v.get("status", "Missing") for k, v in cats.items()},
            "missing_information": [name for name, value in category_rows.items() if value["coverage_status"] in ("Missing", "Not separately scored; inspect source documents")],
            "categories": category_rows,
            "candidate_authoritative_sources": source_candidates,
            "research_status": "not_researched_in_this_operation",
            "enrichment_status": "not_enriched_in_this_operation",
            "research_notes": "The previous lexical coverage report is a triage lead, not proof that any source supports a claim. No page is treated as inspected until its content is recorded in an enrichment document or research log.",
        })
    result = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "catalogue_count": len(catalogue),
        "unique_temple_ids": len({t["id"] for t in catalogue}),
        "existing_knowledge_documents": len(docs),
        "source_registry_unchanged": True,
        "method": "Queue generated from local catalogue, document links and heuristic coverage report. This is a research plan, not external research.",
        "temples": rows,
    }
    output = DATA / "research_plan_all_217.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "temples": len(rows), "documents": len(docs)}, indent=2))


if __name__ == "__main__":
    main()
