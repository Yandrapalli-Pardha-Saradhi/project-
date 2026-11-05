"""Build a claim-evidence-oriented coverage matrix for all catalogue temples.

This is an audit of the local corpus, not factual verification. It does not
fetch sources, change registry approvals, or modify catalogue/documents/index.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CATALOGUE_PATH = DATA / "catalogue.json"
DOCUMENTS_PATH = DATA / "raw" / "temple_sources.json"
OUTPUT_COVERAGE = DATA / "knowledge_coverage_report_final.json"
OUTPUT_ENRICHMENT = DATA / "enrichment_report_all_temples.json"

CATEGORIES = {
    "historical_background": re.compile(r"\b(history|historical|centur(?:y|ies)|dated|constructed|construction|built|commissioned|founded|established|ruler|king|queen|dynast|reign|documented event|attribut(?:e|ed|es|ing))\b", re.I),
    "architecture": re.compile(r"\b(architect(?:ure|ural)|vimana|gopuram|gopura|mandapa|mantapa|sanctum|shikhara|sikhara|tower|pillars?|plan|orientation|carv(?:e|ed|ing)|sculpt(?:ure|ed)|stonework|foundation|material|dravidian|nagara|kalinga|roof(?:s|ed)?|verandah|doorframe|fa[cç]ade|wooden|masonry|columns?)\b", re.I),
    "religious_cultural_significance": re.compile(r"\b(deit(?:y|ies)|dedicated to|enshrin(?:e|ed)|shiva|vishnu|krishna|surya|devi|goddess|worship|religious|sacred|pilgrim|pilgrimage|shaiva|vaishnava|cultural significance|tradition)\b", re.I),
    "festivals_rituals": re.compile(r"\b(festival|ritual|procession|ceremony|celebrat(?:e|ion)|annual observance|brahmotsavam|rath yatra|chithirai|shivaratri|jayanthi|jayanthi|consecration)\b", re.I),
    "inscriptions_historical_evidence": re.compile(r"\b(inscription|inscriptions|epigraphy|epigraphic|copper plate|grant|donor record|script|archaeological evidence)\b", re.I),
    "heritage_conservation": re.compile(r"\b(unesco|world heritage|tentative list|protected monument|archaeological survey|asi\b|conservation|restoration|preservation|management plan|threat|inscribed in)\b", re.I),
    "visitor_information": re.compile(r"\b(visitor|visiting|opening hours|timings|entry fee|admission|ticket|how to reach|approach|airport|railway|bus station|located in|district administration|accessibility|access information)\b", re.I),
}

INVENTORY_MARKERS = ("asi_inventory_listing", "official_inventory_paraphrase", "centrally protected monuments/sites inventory")
NEGATIVE_SENTENCE = re.compile(r"\b(does not|do not|not provided|not specified|unknown|unavailable|no current|not state)\b|\b(?:no|not|without)\b[^.!?]{0,120}\b(?:epigraph|inscription)|\bdistinguish(?:es|ing)?\b[^.!?]{0,120}\bfrom\b[^.!?]{0,80}\b(?:epigraphic|inscriptional) evidence", re.I)


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def clean_sentence(sentence: str) -> str:
    return " ".join(sentence.split())


def score_category(evidence: list[dict]) -> tuple[str, dict]:
    usable = [item for item in evidence if not item["negative_only"]]
    if not usable:
        return "Missing", {"document_count": 0, "source_url_count": 0, "evidence_sentences": 0, "document_ids": [], "source_urls": [], "evidence_excerpts": []}
    doc_ids = sorted({item["document_id"] for item in usable})
    urls = sorted({item["source_url"] for item in usable if item["source_url"]})
    sentences = [sentence for item in usable for sentence in item["sentences"]]
    source_sentences = len(sentences)
    inventory_only = all(item["is_inventory"] for item in usable)
    if inventory_only or source_sentences <= 1:
        status = "Basic"
    elif len(doc_ids) >= 3 and source_sentences >= 5 and len(urls) >= 2:
        status = "Detailed"
    elif len(doc_ids) >= 2 and source_sentences >= 3 and len(urls) >= 2:
        status = "Good"
    else:
        status = "Limited"
    return status, {
        "document_count": len(doc_ids),
        "source_url_count": len(urls),
        "evidence_sentences": source_sentences,
        "document_ids": doc_ids,
        "source_urls": urls,
        "source_types": sorted({item["source_type"] for item in usable if item["source_type"]}),
        "review_statuses": sorted({item["review_status"] for item in usable if item["review_status"]}),
        "evidence_excerpts": sentences[:4],
        "inventory_only": inventory_only,
        "scoring_note": "Automated lexical/source-metadata triage. Evidence sentences are leads for review, not claim validation.",
    }


def analyze(catalogue: list[dict], documents: list[dict]) -> dict:
    docs_by_temple: dict[str, list[dict]] = {}
    for doc in documents:
        if isinstance(doc, dict) and isinstance(doc.get("temple_id"), str):
            docs_by_temple.setdefault(doc["temple_id"], []).append(doc)

    rows = []
    class_counts: Counter[str] = Counter()
    category_counts: dict[str, Counter[str]] = {key: Counter() for key in CATEGORIES}
    for temple in catalogue:
        temple_id = temple["id"]
        linked = docs_by_temple.get(temple_id, [])
        per_category: dict[str, dict] = {}
        for category, pattern in CATEGORIES.items():
            evidence = []
            for doc in linked:
                text = str(doc.get("text") or "")
                topic = str(doc.get("topic") or "")
                marker = f"{topic} {doc.get('source_type', '')} {doc.get('source_title', '')}".casefold()
                is_inventory = any(part in marker for part in INVENTORY_MARKERS)
                # Inventory lists can substantiate only basic place/approach
                # facts; they are not treated as history or temple description.
                if is_inventory and category != "visitor_information":
                    continue
                sentences = [clean_sentence(s) for s in re.split(r"(?<=[.!?])\s+", text) if pattern.search(s)]
                if category == "inscriptions_historical_evidence":
                    # A World Heritage inscription or Tentative List reference
                    # does not establish temple epigraphy. Keep such a
                    # sentence only when it also describes actual inscriptional
                    # evidence (scripts, grants, records, epigraphic findings).
                    direct_epigraphy = re.compile(r"\b(epigraph(?:y|ic)|copper plate|donor record|script|inscriptions?\s+(?:record|records|identify|identified|mention|mentions|document|documents|contain|contains|attest|attests|name|names))\b", re.I)
                    sentences = [s for s in sentences if not re.search(r"\b(?:unesco|world heritage|tentative list)\b", s, re.I) or direct_epigraphy.search(s)]
                negative = [s for s in sentences if NEGATIVE_SENTENCE.search(s)]
                positive = [s for s in sentences if not NEGATIVE_SENTENCE.search(s)]
                # A category tag alone is insufficient; require source text
                # matching that category. Preserve negative gap statements.
                if positive or negative:
                    evidence.append({
                        "document_id": doc.get("document_id", ""),
                        "source_url": doc.get("source_url", ""),
                        "source_type": doc.get("source_type", ""),
                        "review_status": doc.get("review_status") or doc.get("verification_status", ""),
                        "is_inventory": is_inventory,
                        "sentences": positive[:5],
                        "negative_only": not positive,
                    })
            status, detail = score_category(evidence)
            per_category[category] = {"status": status, **detail}
            category_counts[category][status] += 1

        values = [value["status"] for value in per_category.values()]
        statuses = Counter(values)
        if statuses["Detailed"] >= 2 and statuses["Good"] + statuses["Detailed"] >= 4:
            aggregate = "Broadly documented"
        elif statuses["Good"] + statuses["Detailed"] >= 3:
            aggregate = "Several topics documented"
        elif statuses["Missing"] <= 2 and statuses["Limited"] + statuses["Good"] + statuses["Detailed"] >= 3:
            aggregate = "Partial profile"
        elif statuses["Basic"] + statuses["Missing"] >= 4:
            aggregate = "Basic / substantial gaps"
        else:
            aggregate = "Limited profile"
        class_counts[aggregate] += 1
        gaps = [key for key, value in per_category.items() if value["status"] in ("Missing", "Basic", "Limited")]
        rows.append({
            "temple_id": temple_id,
            "name": temple.get("canonical_name") or (temple.get("names") or [temple_id])[0],
            "alternate_names": temple.get("alternate_names") or temple.get("names", []),
            "state": temple.get("state"),
            "district": temple.get("district"),
            "document_count": len(linked),
            "coverage_class_heuristic": aggregate,
            "categories": per_category,
            "research_gaps": gaps,
            "source_domains": sorted({urlsplit(str(d.get("source_url") or "")).hostname or "" for d in linked if d.get("source_url")}),
            "documents_pending_review": sum("pending" in str(d.get("review_status") or d.get("verification_status") or "").casefold() for d in linked),
        })

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "catalogue_count": len(catalogue),
        "knowledge_document_count": len(documents),
        "method": {
            "purpose": "Full-catalogue local evidence audit to prioritize human research.",
            "limitations": [
                "Category ratings are lexical/source-metadata heuristics and are not proof that claims are true or complete.",
                "A source URL is not treated as authoritative solely from its domain; reviewers must check the cited page and claim.",
                "Tentative List nominations are not counted as World Heritage inscriptions.",
                "Current visitor hours, fees and access restrictions require live official confirmation.",
                "Inventory-only documents are not counted as evidence for history, architecture, religion, festivals or conservation.",
            ],
            "status_definitions": {
                "Missing": "No matching source-text evidence found in linked documents.",
                "Basic": "Only basic or one-sentence evidence found; includes inventory-only place information.",
                "Limited": "Some source-text evidence, but sparse, concentrated in a single document, or not corroborated.",
                "Good": "Multiple evidence documents/sentences and at least two source URLs under the heuristic.",
                "Detailed": "At least three evidence documents, five matching sentences and two source URLs under the heuristic.",
            },
        },
        "aggregate_coverage_counts": dict(class_counts),
        "category_status_counts": {key: dict(value) for key, value in category_counts.items()},
        "temples": rows,
    }


def main() -> None:
    catalogue = read(CATALOGUE_PATH)
    documents = read(DOCUMENTS_PATH)
    baseline = analyze(catalogue, [doc for doc in documents if not str(doc.get("document_id", "")).startswith("enrich_batch04_")])
    current = analyze(catalogue, documents)
    operation_prefixes = ("systematic_research_20261105_",)
    operation_baseline = analyze(catalogue, [doc for doc in documents if not str(doc.get("document_id", "")).startswith(operation_prefixes)])
    before = {row["temple_id"]: row for row in baseline["temples"]}
    after = {row["temple_id"]: row for row in current["temples"]}
    changes = Counter()
    for temple_id, row in after.items():
        for category, value in row["categories"].items():
            old = before[temple_id]["categories"][category]["status"]
            new = value["status"]
            if old != new:
                changes[f"{old} -> {new}"] += 1
    current["coverage_improvement_since_batch_04_preindex_baseline"] = dict(changes)
    operation_before = {row["temple_id"]: row for row in operation_baseline["temples"]}
    operation_changes = Counter()
    for temple_id, row in after.items():
        for category, value in row["categories"].items():
            old = operation_before[temple_id]["categories"][category]["status"]
            new = value["status"]
            if old != new:
                operation_changes[f"{old} -> {new}"] += 1
    current["coverage_improvement_this_operation"] = dict(operation_changes)
    current["baseline_before_batch_04"] = {
        "catalogue_count": baseline["catalogue_count"],
        "document_count": baseline["knowledge_document_count"],
        "category_status_counts": baseline["category_status_counts"],
    }
    OUTPUT_COVERAGE.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    registry = read(DATA / "source_registry.json")
    research_plan = read(DATA / "research_plan_all_217.json") if (DATA / "research_plan_all_217.json").exists() else {}
    data_checkpoint = research_plan.get("data_integrity_checkpoint", {})
    actual_source_checks = research_plan.get("source_checks_this_operation", [])
    newly_added_docs = [doc for doc in documents if str(doc.get("document_id", "")).startswith(operation_prefixes)]
    newly_enriched_temple_ids = {doc.get("temple_id") for doc in newly_added_docs}
    temples_with_inspected_pages = [row for row in research_plan.get("temples", []) if row.get("sources_inspected")]
    unresearched_temples = [
        {"temple_id": row["temple_id"], "name": row["canonical_name"]}
        for row in research_plan.get("temples", []) if not row.get("sources_inspected")
    ]
    prior_source_attributed_temples = [
        {"temple_id": row["temple_id"], "name": row["canonical_name"],
         "document_ids": [doc["document_id"] for doc in row.get("prior_source_attributed_documents", [])]}
        for row in research_plan.get("temples", []) if row.get("prior_source_attributed_documents")
    ]
    no_prior_source_document_temples = [
        {"temple_id": row["temple_id"], "name": row["canonical_name"]}
        for row in research_plan.get("temples", []) if not row.get("prior_source_attributed_documents")
    ]
    manifests = [read(path) for path in sorted(DATA.glob("enrichment_manifest_batch_*.json"))]
    previous_scope = {row.get("temple_id") for manifest in manifests for row in manifest.get("temples", []) if row.get("temple_id")}
    orphan_docs = [doc for doc in documents if doc.get("temple_id") not in {t["id"] for t in catalogue}]
    source_counter = Counter(doc.get("source_type") or "unspecified" for doc in documents)
    pending_docs = [doc for doc in documents if "pending" in str(doc.get("review_status") or doc.get("verification_status") or "").casefold()]
    evaluation = read(DATA / "retrieval_evaluation_all_temples.json") if (DATA / "retrieval_evaluation_all_temples.json").exists() else {}
    evaluation_summary = evaluation.get("summary", {})
    plan_by_temple = {row["temple_id"]: row for row in research_plan.get("temples", [])}
    temple_rows = []
    for row in current["temples"]:
        temple_rows.append({
            "temple_id": row["temple_id"],
            "name": row["name"],
            "state": row["state"],
            "district": row["district"],
            "documents_current": row["document_count"],
            "category_statuses": {k: v["status"] for k, v in row["categories"].items()},
            "research_gaps": row["research_gaps"],
            "evidence_urls_by_category": {k: v["source_urls"] for k, v in row["categories"].items() if v["source_urls"]},
            "recommended_next_step": "Manually review authoritative source candidates for each listed gap; confirm source terms and claim-level support before preparing any new document.",
            "priority_for_research": "high" if row["coverage_class_heuristic"] == "Basic / substantial gaps" else "medium" if row["research_gaps"] else "low",
            "already_in_enrichment_manifest": row["temple_id"] in previous_scope,
            "research_status": plan_by_temple.get(row["temple_id"], {}).get("research_status", "not_researched_in_this_operation"),
            "sources_inspected": plan_by_temple.get(row["temple_id"], {}).get("sources_inspected", []),
            "categories_researched": plan_by_temple.get(row["temple_id"], {}).get("categories_researched", []),
            "documents_added_this_operation": plan_by_temple.get(row["temple_id"], {}).get("documents_added_this_operation", []),
            "remaining_gaps": plan_by_temple.get(row["temple_id"], {}).get("remaining_gaps", row["research_gaps"]),
            "error_or_access_limitations": plan_by_temple.get(row["temple_id"], {}).get("error_or_access_limitations", []),
            "prior_source_attributed_documents": plan_by_temple.get(row["temple_id"], {}).get("prior_source_attributed_documents", []),
            "prior_enrichment_manifest_batches": plan_by_temple.get(row["temple_id"], {}).get("prior_enrichment_manifest_batches", []),
        })
    current_by_temple = {row["temple_id"]: row for row in current["temples"]}
    new_docs_by_temple: dict[str, list[str]] = {}
    current_doc_counts = Counter(doc.get("temple_id") for doc in documents)
    for doc in newly_added_docs:
        new_docs_by_temple.setdefault(doc.get("temple_id"), []).append(doc.get("document_id"))
    for plan_row in research_plan.get("temples", []):
        tid = plan_row["temple_id"]
        plan_row["current_document_count_after_checkpoint"] = current_doc_counts.get(tid, 0)
        audited = current_by_temple.get(tid)
        if audited:
            plan_row["coverage_after_checkpoint_heuristic"] = {key: value["status"] for key, value in audited["categories"].items()}
        if tid in new_docs_by_temple:
            plan_row["enrichment_status"] = "source_attributed_documents_added_pending_human_review"
            plan_row["documents_added_this_operation"] = sorted(new_docs_by_temple[tid])
            plan_row["documents_added"] = sorted(set(plan_row.get("documents_added", [])) | set(new_docs_by_temple[tid]))
    research_plan["current_knowledge_document_count"] = len(documents)
    research_plan["new_documents_added_this_operation"] = len(newly_added_docs)
    research_plan["temples_with_new_documents_pending_review"] = len(newly_enriched_temple_ids)
    research_plan["last_updated_utc"] = datetime.now(timezone.utc).isoformat()
    (DATA / "research_plan_all_217.json").write_text(json.dumps(research_plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    enrichment = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "operation_status": "PARTIAL_SOURCE_RESEARCH_CHECKPOINT_ENRICHMENT_INCOMPLETE",
        "temples_audited": len(temple_rows),
        "temples_researched_with_pages_inspected_in_this_operation": len(temples_with_inspected_pages),
        "temples_fully_researched_in_this_operation": 0,
        "temples_with_partial_source_research": len(temples_with_inspected_pages),
        "temples_without_source_pages_inspected_in_this_operation": len(unresearched_temples),
        "unresearched_temple_ids_and_names": unresearched_temples,
        "temples_with_prior_source_attributed_documents": len(prior_source_attributed_temples),
        "prior_source_attributed_temple_ids_and_documents": prior_source_attributed_temples,
        "temples_with_prior_source_documents_not_opened_this_operation": research_plan.get("prior_source_attributed_but_not_opened_this_operation_count", 0),
        "temples_without_prior_noninventory_source_documents": len(no_prior_source_document_temples),
        "temples_without_prior_noninventory_source_document_ids_and_names": no_prior_source_document_temples,
        "temples_with_source_supported_new_documents_added_in_this_operation": len(newly_enriched_temple_ids),
        "documents_added_in_this_operation": len(newly_added_docs),
        "documents_modified_in_this_operation": len(data_checkpoint.get("updated_document_ids", [])),
        "updated_document_ids_in_this_operation": data_checkpoint.get("updated_document_ids", []),
        "indexing_checkpoint": data_checkpoint,
        "sources_accessed_in_this_operation": actual_source_checks,
        "source_access_attempts_not_used_as_evidence": research_plan.get("inaccessible_or_unmapped_source_attempts", []),
        "remaining_temple_research_gaps": [{"temple_id": row["temple_id"], "name": row["name"], "categories": row["research_gaps"]} for row in temple_rows],
        "new_document_review_status": {"pending_human_review": sum(doc.get("review_status") == "pending_human_review" for doc in newly_added_docs)},
        "retrieval_evaluation_summary": {
            "evaluation_file": "retrieval_evaluation_all_temples.json",
            "temple_name_queries_passed": evaluation_summary.get("temple_name_queries_passed"),
            "topic_queries": evaluation_summary.get("topic_queries"),
            "evidence_available_category_queries": evaluation_summary.get("evidence_available_category_queries"),
            "evidence_available_category_queries_passed": evaluation_summary.get("evidence_available_category_queries_passed"),
            "unsupported_category_queries": evaluation_summary.get("unsupported_category_queries"),
            "unsupported_category_queries_with_potential_other_context": evaluation_summary.get("unsupported_category_queries_with_potential_other_context"),
            "citation_metadata_matches": evaluation_summary.get("citation_metadata_matches"),
            "citation_metadata_checks": evaluation_summary.get("citation_metadata_checks"),
            "similar_name_resolution_passed": evaluation_summary.get("similar_name_resolution_passed"),
            "external_llm_called": evaluation_summary.get("external_llm_called"),
        },
        "source_references_already_present_in_corpus": [
            {"source_type": source_type, "document_count": count}
            for source_type, count in sorted(source_counter.items())
        ],
        "catalogue_records_added_or_removed": 0,
        "existing_batch_scope_unique_temple_count": len(previous_scope),
        "existing_documents_pending_review": len(pending_docs),
        "processing_errors": [],
        "source_breakdown_by_existing_source_type": dict(source_counter),
        "source_registry_snapshot": [
            {"id": source.get("id"), "enabled": source.get("enabled"), "terms_review_status": source.get("terms_review_status"), "permitted_collection_method": source.get("permitted_collection_method")}
            for source in registry.get("sources", [])
        ],
        "unlinked_general_heritage_documents_preserved": [doc.get("document_id") for doc in orphan_docs],
        "limitation": "This is a partial research checkpoint, not completion of the all-temple task. Only catalogue records linked in research_plan_all_217.json have source pages inspected in this operation. The other temples remain unresearched here. The source registry was not changed and no automated collection was run. New documents remain pending human review.",
        "temples": temple_rows,
    }
    OUTPUT_ENRICHMENT.write_text(json.dumps(enrichment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "coverage_report": str(OUTPUT_COVERAGE),
        "enrichment_report": str(OUTPUT_ENRICHMENT),
        "catalogue": len(catalogue), "documents": len(documents),
        "coverage": current["aggregate_coverage_counts"],
        "category_status_counts": current["category_status_counts"],
        "new_documents_this_operation": len(newly_added_docs),
        "unlinked_general_documents_preserved": len(orphan_docs),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
