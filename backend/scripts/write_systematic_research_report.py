"""Write a readable, resumable partial checkpoint report from machine reports."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def main() -> None:
    plan = load("research_plan_all_217.json")
    coverage = load("knowledge_coverage_report_final.json")
    enrichment = load("enrichment_report_all_temples.json")
    evaluation = load("retrieval_evaluation_all_temples.json")
    summary = evaluation.get("summary", {})
    rows = plan.get("temples", [])
    name_failures = [
        (temple.get("name") or temple.get("temple_id"), test.get("question"))
        for temple in evaluation.get("temples", [])
        for test in temple.get("tests", [])
        if test.get("category") == "temple_name" and not test.get("retrieval_success")
    ]
    topic_failures = [
        (temple.get("name") or temple.get("temple_id"), test.get("category"), test.get("outcome"))
        for temple in evaluation.get("temples", [])
        for test in temple.get("tests", [])
        if test.get("outcome") == "expected_topic_evidence_not_retrieved"
    ]
    missing_page = [r for r in rows if not r.get("sources_inspected")]
    inspected = [r for r in rows if r.get("sources_inspected")]
    status_counts = plan.get("queue_status_counts", {})
    source_map = plan.get("source_reuse_index", {}).get("sources", [])
    inspected_sources = [s for s in source_map if s.get("page_inspected_for_temple_ids")]
    category_counts = coverage.get("category_status_counts", {})
    aggregate = coverage.get("aggregate_coverage_counts", {})
    data_checkpoint = plan.get("data_integrity_checkpoint", {})
    lines = [
        "# All-Temple Research Coverage — Resumable Checkpoint",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "> **Incomplete.** This checkpoint does not meet the all-217 source-research completion condition. It records only source pages actually opened and read, with source relationships kept temple-specific.",
        "",
        "## Verified state",
        "",
        f"- Catalogue: **{plan.get('catalogue_count')} records** ({plan.get('unique_temple_ids')} unique IDs). No records were added or removed.",
        f"- Curated knowledge documents: **{plan.get('current_knowledge_document_count')}**.",
        f"- Persistent `temple_heritage` collection: **{data_checkpoint.get('collection_chunk_count', evaluation.get('collection_chunk_count'))} chunks** at `{data_checkpoint.get('collection', evaluation.get('collection_name'))}`.",
        f"- Actually inspected source URLs recorded across the queue history: **{plan.get('source_reuse_index', {}).get('actually_inspected_url_count', len(inspected_sources))} unique URLs**; {len(inspected_sources)} were linked to specific temple records, while general-purpose pages are tracked separately.",
        f"- Catalogue temples with at least one recorded source page inspected: **{len(inspected)} / 217**. All {len(inspected)} remain partial and have outstanding topic gaps.",
        f"- Catalogue temples without a relevant source page inspected in this operation: **{len(missing_page)} / 217**. This includes {status_counts.get('evidence_extracted', 0)} with source-attributed corpus documents whose actual source pages were not confirmed inspected here.",
        f"- Queue status: {', '.join(f'{key}={value}' for key, value in status_counts.items())}.",
        f"- New source-attributed documents added in this operation: **{enrichment.get('documents_added_in_this_operation')}**, linked to **{enrichment.get('temples_with_source_supported_new_documents_added_in_this_operation')}** temples. New documents are `pending_human_review`; no document was marked verified.",
        f"- Documents modified after their first index: **{enrichment.get('documents_modified_in_this_operation', 0)}**. Source registry permissions were unchanged; no automated collection was run.",
        "",
        "The source-gate workflow was respected. Research used identified government, UNESCO, ASI, state-tourism and institutional pages that were opened individually. The Himachal Tourism page returned HTTP 200 and its temple-specific text was read; the web extractor timed out, so the page was inspected through a direct single-page request. A source that named a similarly named temple at a conflicting locality was not attached as evidence.",
        "",
        "## Coverage snapshot",
        "",
        "Aggregate heuristic classes (not factual completeness):",
        "",
    ]
    lines.extend(f"- {name}: **{count}**" for name, count in aggregate.items())
    lines += ["", "Category statuses (heuristic corpus evidence, not verified facts):", ""]
    for category, counts in category_counts.items():
        lines.append(f"- `{category}`: " + ", ".join(f"{key} {value}" for key, value in counts.items()))
    lines += [
        "",
        "## Retrieval evaluation",
        "",
        f"- Name queries: **{summary.get('temple_name_queries_passed')} / {summary.get('temple_name_queries')}** passed.",
        f"- Topic retrieval queries: **{summary.get('topic_queries')}**; evidence-available queries passed **{summary.get('evidence_available_category_queries_passed')} / {summary.get('evidence_available_category_queries')}**.",
        f"- Unsupported-topic queries: **{summary.get('unsupported_category_queries')}**; potential unrelated context admitted: **{summary.get('unsupported_category_queries_with_potential_other_context')}**.",
        f"- Source URL metadata matched the local document record in **{summary.get('citation_metadata_matches')} / {summary.get('citation_metadata_checks')}** checks. This validates metadata linkage, not whether a generated answer is factually supported by that page.",
        f"- Follow-up scope: **{summary.get('followup_scope_passed')} / {summary.get('followup_questions')}**. Similar-name resolution: **{summary.get('similar_name_resolution_passed')} / {summary.get('similar_name_scope_checks')}**; metadata scope checks passed **{summary.get('similar_name_metadata_filter_passed')} / {summary.get('similar_name_scope_checks')}**.",
        f"- External LLM called: **{summary.get('external_llm_called')}**. Retrieval evaluation does not establish generated-answer accuracy.",
        "",
        "Name-query failures: " + ("; ".join(f"{name} ({question})" for name, question in name_failures) if name_failures else "none."),
        "Expected-topic retrieval mismatches: " + ("; ".join(f"{name}, {category}: {outcome}" for name, category, outcome in topic_failures) if topic_failures else "none."),
        "",
        "## Incremental indexing and validation",
        "",
        f"- Curated document validation: **{enrichment.get('catalogue_records_added_or_removed', 0)} catalogue changes**, catalog remains 217; final document validation reported no errors and no duplicate content before indexing.",
        f"- Current collection: **{data_checkpoint.get('collection_chunk_count')} chunks**. This operation added **{data_checkpoint.get('indexing', {}).get('new_documents_added_this_operation')} documents**. After first indexing, **{data_checkpoint.get('indexing', {}).get('documents_text_modified_after_first_index')} documents** were tightened to avoid caveat text being misread as evidence.",
        f"- Latest two dry runs agreed: {data_checkpoint.get('indexing', {}).get('latest_dry_run_chunks_updated')} chunk updates, {data_checkpoint.get('indexing', {}).get('latest_dry_run_metadata_only_updates')} metadata-only updates and {data_checkpoint.get('indexing', {}).get('latest_dry_run_stale_chunks_removed')} obsolete chunks from those modified document versions removed. No unrelated chunks were deleted.",
        "- The Chroma collection was not reset. All document additions remain pending human review.",
        "",
        "## Sources actually inspected",
        "",
    ]
    for source in inspected_sources:
        links = ", ".join(source.get("page_inspected_for_temple_ids", []))
        lines.append(f"- [{source.get('source_title') or source.get('source_url')}]({source.get('source_url')}) — inspected for: {links}")
    lines += [
        "",
        "## Temples still needing an inspected source page",
        "",
        f"These {len(missing_page)} IDs have not yet had a relevant external page inspected in this operation ({status_counts.get('evidence_extracted', 0)} have source-attributed corpus documents whose original pages were not confirmed inspected here; the list is exact and resumable):",
        "",
    ]
    for row in missing_page:
        name = row.get("canonical_name") or row.get("temple_name") or row.get("temple_id")
        location = ", ".join(x for x in [row.get("district"), row.get("state")] if x)
        lines.append(f"- `{row['temple_id']}` — **{name}**" + (f" ({location})" if location else "") + f" — status: `{row.get('research_status')}`")
    lines += [
        "",
        "## Partially researched temples and remaining gaps",
        "",
        "The following temples have at least one inspected source page, but none has a complete seven-topic research profile. Their exact outstanding category gaps are recorded below.",
        "",
    ]
    for row in inspected:
        gaps = row.get("missing_categories") or row.get("remaining_gaps") or []
        name = row.get("canonical_name") or row.get("temple_name") or row.get("temple_id")
        lines.append(f"- `{row['temple_id']}` — **{name}** — gaps: {', '.join(gaps) if gaps else 'coverage needs claim-level review'}")
    lines += [
        "",
        "## Verification and known limitations",
        "",
        "- New source claims are paraphrases pending human review. Opened pages and source metadata were checked; this does not constitute independent historical verification.",
        "- Conflicting chronology for Chamba's Lakshmi Narayan complex (state government pilgrimage page: broad 8th-century group date; state tourism page: main Vishnu shrine attributed to Sahil Varman in the 10th century) is preserved in the documents for review.",
        "- The 2019 Masroor project profile and Himachal Tourism page differ on the number of rock-cut temples (19 versus 15); both accounts are disclosed in the document.",
        "- The official Himachal Tourism Trilokinath entry describes an Udaipur, Lahaul-Spiti shrine, whereas the catalogue record is localized to Mandi. It was not attached; the mismatch is in the research plan.",
        f"- Retrieval context admission is evaluated locally. The latest report records {summary.get('unsupported_category_queries_with_potential_other_context')} potentially unrelated contexts among {summary.get('unsupported_category_queries')} unsupported-topic queries. A previous one-off name-query miss for Debi dole did not repeat on the latest full run (name-query success: {summary.get('temple_name_queries_passed')}/{summary.get('temple_name_queries')}).",
        "- A candidate Assam Directorate of Archaeology protected-sites page returned HTTP 404 on direct access; the search result was not used as evidence and the failed attempt is recorded in the research plan.",
        "- Source pages for festival dates, visitor timings, fees and access were not assumed current unless explicitly dated by the page. No OpenRouter call was made.",
        "",
        "## Test and command record",
        "",
        f"- `python -m app.ingestion validate`: passed for {plan.get('current_knowledge_document_count')} curated documents and {plan.get('catalogue_count')} catalogue records; pending human-review warnings are expected.",
        f"- `python -m app.ingestion index --dry-run`: latest consecutive dry runs matched; {data_checkpoint.get('indexing', {}).get('latest_dry_run_documents_added')} documents / {data_checkpoint.get('indexing', {}).get('latest_dry_run_chunks_added')} chunks to add, with {data_checkpoint.get('collection_chunk_count')} existing chunks unchanged.",
        f"- `python -m app.ingestion index`: completed incrementally; latest collection count is {data_checkpoint.get('collection_chunk_count')}.",
        f"- `python scripts/evaluate_retrieval_all_temples.py`: local retrieval only; {summary.get('temple_name_queries_passed')}/{summary.get('temple_name_queries')} name queries, {summary.get('evidence_available_category_queries_passed')}/{summary.get('evidence_available_category_queries')} evidence-available topic queries, {summary.get('citation_metadata_matches')}/{summary.get('citation_metadata_checks')} citation metadata matches. No OpenRouter call was made.",
        "- Backend pytest and Python compilation results are recorded in the current work log; frontend files were not changed.",
        "",
        "## Resume instructions",
        "",
        "Use `research_plan_all_217.json` as the authoritative queue. Continue first with rows whose `sources_inspected` list is empty, then re-research the inspected rows' `missing_categories`. Verify any candidate page before adding its URL to `source_checks_this_operation`; do not treat corpus citations or a source URL alone as inspected evidence. Save a backup and checkpoint after every small group.",
        "",
    ]
    out = DATA / "FINAL_KNOWLEDGE_ENRICHMENT_REPORT.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"report": str(out), "without_inspected_page": len(missing_page), "partially_researched": len(inspected), "temple_linked_source_pages": len(inspected_sources), "unique_inspected_source_urls": plan.get("source_reuse_index", {}).get("actually_inspected_url_count")}, indent=2))


if __name__ == "__main__":
    main()
