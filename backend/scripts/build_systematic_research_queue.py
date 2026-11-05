"""Rebuild the resumable 217-temple queue from catalogue and provenance."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PLAN_PATH = DATA / "research_plan_all_217.json"
DOC_PATH = DATA / "raw" / "temple_sources.json"
CHECKED_PREFIXES = ("asi_inventory_",)
CURRENT_DOC_PREFIXES = ("resume_research_20261105_", "systematic_research_20261105_")
RESEARCHED_CATEGORY_BY_TOPIC = {
    "history": "historical_background", "historical": "historical_background",
    "architecture": "architecture", "architectural": "architecture",
    "deity": "religious_cultural_significance", "religious": "religious_cultural_significance",
    "culture": "religious_cultural_significance", "festival": "festivals_traditions",
    "ritual": "festivals_traditions", "inscription": "inscriptions_historical_evidence",
    "epigraph": "inscriptions_historical_evidence", "heritage": "heritage_conservation",
    "conservation": "heritage_conservation", "visitor": "visitor_information",
    "access": "visitor_information",
}
CATEGORIES = [
    "historical_background", "architecture", "religious_cultural_significance",
    "festivals_traditions", "inscriptions_historical_evidence",
    "heritage_conservation", "visitor_information",
]


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def topics_from_doc(doc: dict) -> set[str]:
    text = f"{doc.get('topic') or ''} {doc.get('title') or ''}".casefold()
    return {category for marker, category in RESEARCHED_CATEGORY_BY_TOPIC.items() if marker in text}


def is_inventory(doc: dict) -> bool:
    return (
        str(doc.get("document_id") or "").startswith(CHECKED_PREFIXES)
        or "inventory" in str(doc.get("source_type") or "").casefold()
        or "centrally protected monuments/sites" in str(doc.get("source_title") or "").casefold()
    )


def main() -> None:
    plan = read(PLAN_PATH)
    catalogue = read(DATA / "catalogue.json")
    docs = read(DOC_PATH)
    coverage = read(DATA / "knowledge_coverage_report_final.json")
    catalog_by_id = {row["id"]: row for row in catalogue}
    plan_by_id = {row["temple_id"]: row for row in plan.get("temples", [])}
    coverage_by_id = {row["temple_id"]: row for row in coverage.get("temples", [])}
    docs_by_id: dict[str, list[dict]] = defaultdict(list)
    for doc in docs:
        if doc.get("temple_id") in catalog_by_id:
            docs_by_id[doc["temple_id"]].append(doc)

    # These entries assert page inspection; document URLs alone do not.
    inspected: dict[str, dict] = {}

    def add_inspected(source: dict, temple_ids: list[str], batch: str | None = None) -> None:
        url = source.get("source_url") or source.get("url")
        if not isinstance(url, str) or not url.startswith(("https://", "http://")):
            return
        entry = inspected.setdefault(url, {
            "source_url": url, "source_title": source.get("source_title") or source.get("title"),
            "publisher": source.get("publisher"), "source_type": source.get("source_type"),
            "publication_date": source.get("publication_date"),
            "accessed_dates": [], "temple_ids_actually_checked": [],
            "categories_supported_by_inspected_source": [], "inspection_evidence": [],
        })
        if source.get("accessed_date"):
            entry["accessed_dates"].append(source["accessed_date"])
        if source.get("inspection_method"):
            entry["inspection_evidence"].append(source["inspection_method"])
        if source.get("note"):
            entry["inspection_evidence"].append(source["note"])
        if batch:
            entry.setdefault("prior_manifest_batches", []).append(batch)
        for temple_id in temple_ids:
            if temple_id in catalog_by_id and temple_id not in entry["temple_ids_actually_checked"]:
                entry["temple_ids_actually_checked"].append(temple_id)
        cats = source.get("categories_with_relevant_source_content") or []
        entry["categories_supported_by_inspected_source"] = sorted(set(entry["categories_supported_by_inspected_source"]) | set(cats))

    for source in plan.get("source_checks_this_operation", []):
        add_inspected(source, source.get("linked_temple_ids", []), "all217_checkpoint_or_resume")

    manifests = sorted(DATA.glob("enrichment_manifest_batch_*.json"))
    manifest_doc_ids: dict[str, set[str]] = defaultdict(set)
    manifest_batches: dict[str, set[str]] = defaultdict(set)
    manifest_notes: dict[str, list[str]] = defaultdict(list)
    for path in manifests:
        batch_name = path.stem.replace("enrichment_manifest_", "")
        manifest = read(path)
        for row in manifest.get("temples", []):
            temple_id = row.get("temple_id")
            if temple_id not in catalog_by_id:
                continue
            manifest_batches[temple_id].add(batch_name)
            for key in ("document_ids", "document_ids_added"):
                for doc_id in row.get(key, []) or []:
                    manifest_doc_ids[temple_id].add(doc_id)
            for key in ("draft_document_id", "document_id_added"):
                if row.get(key):
                    manifest_doc_ids[temple_id].add(row[key])
            if row.get("review_notes"):
                manifest_notes[temple_id].append(str(row["review_notes"]))
            if row.get("verification_note"):
                manifest_notes[temple_id].append(str(row["verification_note"]))
            if row.get("source_notes"):
                manifest_notes[temple_id].extend(str(x) for x in row["source_notes"])
            for source in row.get("sources_actually_checked", []) or []:
                add_inspected(source, [temple_id], batch_name)
            # Batch 1 records explicitly say when candidate source pages were checked.
            if "source checked" in str(row.get("review_notes") or "").casefold():
                for candidate in row.get("candidate_authoritative_sources", []) or []:
                    if isinstance(candidate, str):
                        candidate = {"url": candidate}
                    add_inspected(candidate, [temple_id], batch_name)

    for url, source in inspected.items():
        source["temple_ids_actually_checked"] = sorted(set(source["temple_ids_actually_checked"]))
        source["accessed_dates"] = sorted(set(source["accessed_dates"]))
        source["inspection_evidence"] = sorted(set(source["inspection_evidence"]))
        source["prior_manifest_batches"] = sorted(set(source.get("prior_manifest_batches", [])))

    source_reuse: dict[str, dict] = {}
    for doc in docs:
        url = doc.get("source_url")
        temple_id = doc.get("temple_id")
        if not isinstance(url, str) or not url.startswith(("https://", "http://")) or temple_id not in catalog_by_id:
            continue
        entry = source_reuse.setdefault(url, {
            "source_url": url,
            "source_title": doc.get("source_title") or doc.get("title"),
            "publisher": doc.get("publisher"),
            "source_type": doc.get("source_type"),
            "document_ids": [], "temple_ids_with_cited_documents": [],
            "topics_in_cited_documents": [], "page_inspected_for_temple_ids": [],
            "page_inspection_status": "cited_in_corpus_only_not_assumed_inspected",
        })
        if doc.get("document_id") not in entry["document_ids"]:
            entry["document_ids"].append(doc.get("document_id"))
        if temple_id not in entry["temple_ids_with_cited_documents"]:
            entry["temple_ids_with_cited_documents"].append(temple_id)
        topic = doc.get("topic")
        if topic and topic not in entry["topics_in_cited_documents"]:
            entry["topics_in_cited_documents"].append(topic)

    for url, inspected_row in inspected.items():
        entry = source_reuse.setdefault(url, {
            "source_url": url, "source_title": inspected_row.get("source_title"),
            "publisher": inspected_row.get("publisher"), "source_type": inspected_row.get("source_type"),
            "document_ids": [], "temple_ids_with_cited_documents": [], "topics_in_cited_documents": [],
            "page_inspected_for_temple_ids": [],
        })
        entry["page_inspection_status"] = "actually_inspected_for_linked_temple_ids"
        entry["page_inspected_for_temple_ids"] = inspected_row["temple_ids_actually_checked"]
        entry["inspection_evidence"] = inspected_row["inspection_evidence"]

    status_counts: Counter[str] = Counter()
    queue = []
    for temple in catalogue:
        temple_id = temple["id"]
        row = plan_by_id.get(temple_id, {})
        coverage_row = coverage_by_id.get(temple_id, {})
        linked_docs = docs_by_id.get(temple_id, [])
        temple_checked = sorted(url for url, s in inspected.items() if temple_id in s["temple_ids_actually_checked"])
        categories_from_pages = {
            category for url, s in inspected.items() if temple_id in s["temple_ids_actually_checked"]
            for category in s.get("categories_supported_by_inspected_source", [])
        }
        substantive_docs = [doc for doc in linked_docs if not is_inventory(doc) and doc.get("source_url")]
        categories_from_docs = set().union(*(topics_from_doc(doc) for doc in substantive_docs)) if substantive_docs else set()
        coverage_categories = coverage_row.get("categories", {})
        missing_categories = [
            category for category in CATEGORIES
            if coverage_categories.get(category, {}).get("status", "Missing") in {"Missing", "Basic", "Limited"}
        ]
        research_queries = [
            f'"{temple.get("canonical_name") or (temple.get("names") or [temple_id])[0]}" {temple.get("city") or temple.get("area") or ""} {temple.get("district") or ""} official history archaeology'.strip(),
            f'"{temple.get("canonical_name") or (temple.get("names") or [temple_id])[0]}" architecture inscriptions ASI archaeology'.strip(),
            f'"{temple.get("canonical_name") or (temple.get("names") or [temple_id])[0]}" official festival rituals temple administration'.strip(),
            f'"{temple.get("canonical_name") or (temple.get("names") or [temple_id])[0]}" conservation heritage protected monument official'.strip(),
            f'"{temple.get("canonical_name") or (temple.get("names") or [temple_id])[0]}" official visitor timings access'.strip(),
        ]
        added_ids = sorted({
            doc["document_id"] for doc in linked_docs
            if doc.get("document_id", "").startswith(("all217_research_20261105_", "resume_research_20261105_", "systematic_research_20261105_"))
        } | manifest_doc_ids.get(temple_id, set()))
        attempted_failures = [attempt for attempt in plan.get("inaccessible_or_unmapped_source_attempts", [])
                              if temple_id in attempt.get("linked_temple_ids", [])]
        if any(doc.get("document_id", "").startswith(CURRENT_DOC_PREFIXES) for doc in linked_docs):
            status = "enriched"
        elif temple_checked:
            status = "source_inspected"
        elif substantive_docs:
            status = "evidence_extracted"
        elif attempted_failures:
            status = "source_gap"
        else:
            status = "not_started"
        status_counts[status] += 1
        retrieval_dates = [
            str(doc.get("retrieval_date") or doc.get("collection_timestamp") or "")[:10]
            for doc in linked_docs if doc.get("retrieval_date") or doc.get("collection_timestamp")
        ]
        research_notes = row.get("research_notes", [])
        if isinstance(research_notes, str):
            research_notes = [research_notes] if research_notes else []
        research_notes = list(dict.fromkeys([*research_notes, *manifest_notes.get(temple_id, [])]))
        queue.append({
            "temple_id": temple_id,
            "canonical_name": temple.get("canonical_name") or (temple.get("names") or [temple_id])[0],
            "temple_name": temple.get("canonical_name") or (temple.get("names") or [temple_id])[0],
            "state": temple.get("state"),
            "district": temple.get("district"),
            "existing_document_count": len(linked_docs),
            "previously_inspected_source_urls": temple_checked,
            "sources_inspected": temple_checked,
            "source_urls_in_documents_not_confirmed_inspected": sorted({d.get("source_url") for d in substantive_docs if d.get("source_url")} - set(temple_checked)),
            "previously_researched_categories": sorted(categories_from_pages | categories_from_docs),
            "categories_researched": sorted(categories_from_pages | categories_from_docs),
            "page_evidence_categories": sorted(categories_from_pages),
            "document_topic_categories_heuristic": sorted(categories_from_docs),
            "coverage_status_by_category_heuristic": {cat: coverage_categories.get(cat, {}).get("status", "Missing") for cat in CATEGORIES},
            "missing_categories": missing_categories,
            "remaining_gaps": missing_categories,
            "research_queries_required": research_queries,
            "research_status": status,
            "number_of_sources_actually_inspected": len(temple_checked),
            "research_notes": research_notes,
            "documents_added": added_ids,
            "documents_added_this_operation": [doc_id for doc_id in added_ids if doc_id.startswith(CURRENT_DOC_PREFIXES)],
            "prior_source_attributed_documents": [
                {"document_id": doc.get("document_id"), "source_url": doc.get("source_url"), "source_title": doc.get("source_title"), "topic": doc.get("topic")}
                for doc in substantive_docs if doc.get("document_id") not in added_ids
            ],
            "prior_enrichment_manifest_batches": sorted(manifest_batches.get(temple_id, set())),
            "source_checks": [s for s in inspected.values() if temple_id in s["temple_ids_actually_checked"]],
            "enrichment_status": status,
            "coverage_after_checkpoint_heuristic": coverage_row.get("aggregate_coverage"),
            "last_completed_checkpoint": max(retrieval_dates) if retrieval_dates else None,
            "access_limitations": attempted_failures,
            "error_or_access_limitations": attempted_failures,
        })

    plan["queue_version"] = 2
    plan["queue_generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    plan["queue_status_counts"] = dict(status_counts)
    plan["queue_temple_count"] = len(queue)
    catalogue_temple_ids = set(catalog_by_id)
    prior_source_ids = {
        temple_id for temple_id, temple_docs in docs_by_id.items()
        if any(not is_inventory(doc) and doc.get("source_url") for doc in temple_docs)
    }
    inspected_temple_ids = {temple_id for source in inspected.values() for temple_id in source["temple_ids_actually_checked"]}
    plan["prior_source_attributed_temple_count"] = len(prior_source_ids)
    plan["prior_source_attributed_temple_ids"] = sorted(prior_source_ids)
    plan["prior_source_attributed_but_not_opened_this_operation_count"] = len(prior_source_ids - inspected_temple_ids)
    plan["temples_without_prior_noninventory_source_document_count"] = len(catalogue_temple_ids - prior_source_ids)
    plan["temples_without_prior_noninventory_source_document_ids"] = sorted(catalogue_temple_ids - prior_source_ids)
    plan["temples_without_source_page_inspected_count"] = len(catalogue_temple_ids - inspected_temple_ids)
    plan["temples_without_source_page_inspected_ids"] = sorted(catalogue_temple_ids - inspected_temple_ids)
    plan["temples"] = queue
    plan["source_reuse_index"] = {
        "note": "Only URLs in actually inspected source checks/manifests are marked inspected. Corpus URLs alone remain unconfirmed; each source-temple relationship is listed explicitly.",
        "source_url_count": len(source_reuse),
        "actually_inspected_url_count": len(inspected),
        "sources": [source_reuse[url] for url in sorted(source_reuse)],
    }
    plan["research_status_note"] = (
        "Persistent queue rebuilt from catalogue, current source checks, previous batch manifests, raw document provenance, and heuristic coverage. "
        "No temple is marked researched solely from a source URL. Continue with not_started temples first; category gaps remain open unless evidence is documented."
    )
    PLAN_PATH.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "temples": len(queue), "status_counts": status_counts,
        "source_urls_in_reuse_index": len(source_reuse), "actually_inspected_urls": len(inspected),
        "pages_linked_to_temple_records": sum(bool(row["previously_inspected_source_urls"]) for row in queue),
        "not_started": status_counts.get("not_started", 0),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
