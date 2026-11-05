"""Evaluate indexed evidence and citation metadata across all 217 temples.

The evaluator uses the persistent Chroma collection and the configured local
embedding model. It does not call OpenRouter or the web-search service.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

import chromadb
from app.config import Settings
from app.schemas.chat import ConversationMessage
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.retrieval_service import RetrievedChunk, RetrievalService
from app.services.web_search_service import WebSearchService

DATA = BACKEND / "data"
OUTPUT = DATA / "retrieval_evaluation_all_temples.json"
TOPIC_PATTERNS = {
    "historical_background": re.compile(r"\b(history|historical|centur(?:y|ies)|dated|constructed|construction|built|commissioned|founded|established|ruler|king|queen|dynast|reign|documented event|attribut(?:e|ed|es|ing))\b", re.I),
    "architecture": re.compile(r"\b(architect(?:ure|ural)|vimana|gopuram|gopura|mandapa|mantapa|sanctum|shikhara|sikhara|tower|pillars?|plan|orientation|carv(?:e|ed|ing)|sculpt(?:ure|ed)|stonework|foundation|material|dravidian|nagara|kalinga|roof(?:s|ed)?|verandah|doorframe|fa[cç]ade|wooden|masonry|columns?)\b", re.I),
    "religious_cultural_significance": re.compile(r"\b(deit(?:y|ies)|dedicated to|enshrin(?:e|ed)|shiva|vishnu|krishna|surya|devi|goddess|worship|religious|sacred|pilgrim|pilgrimage|shaiva|vaishnava|cultural significance|tradition)\b", re.I),
    "festivals_rituals": re.compile(r"\b(festival|ritual|procession|ceremony|celebrat(?:e|ion)|annual observance|brahmotsavam|rath yatra|chithirai|shivaratri|jayanthi|consecration)\b", re.I),
    "inscriptions_historical_evidence": re.compile(r"\b(inscriptions?|epigraphs?|inscribed|copper plate|grants?|donor records?|script|archaeological evidence)\b", re.I),
    "heritage_conservation": re.compile(r"\b(unesco|world heritage|tentative list|protected monument|archaeological survey|asi\b|conservation|restoration|preservation|management plan|threat|inscribed in)\b", re.I),
    "visitor_information": re.compile(r"\b(visitor|visiting|opening hours|timings|entry fee|admission|ticket|how to reach|approach|airport|railway|bus station|located in|district administration|accessibility|access information)\b", re.I),
}
CATEGORY_QUESTIONS = {
    "historical_background": "What historical background, chronology and rulers are documented for {name}?",
    "architecture": "What architectural style and structural features are documented for {name}?",
    "religious_cultural_significance": "What deity and religious or cultural significance are documented for {name}?",
    "festivals_rituals": "What festivals, rituals or traditions are documented for {name}?",
    "inscriptions_historical_evidence": "What inscriptions, scripts, grants or epigraphic records are documented for {name}?",
    "heritage_conservation": "What heritage status or conservation history is documented for {name}?",
    "visitor_information": "What official visitor and access information is documented for {name}?",
}
NAME_QUERY = "What is {name} and where is it located?"
FOLLOWUP_QUESTION = "What is special about this temple?"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_name(value: str) -> str:
    value = re.sub(r"[^a-z0-9 ]", " ", value.casefold())
    ignored = {"temple", "temples", "group", "complex", "at", "the", "of", "and", "shri", "sri"}
    return " ".join(token for token in value.split() if token not in ignored)


def main() -> None:
    settings = Settings()
    catalogue = read(DATA / "catalogue.json")
    coverage = read(DATA / "knowledge_coverage_report_final.json")
    corpus = read(DATA / "raw" / "temple_sources.json")
    coverage_by_id = {row["temple_id"]: row for row in coverage["temples"]}
    source_by_doc = {row.get("document_id"): row for row in corpus if row.get("document_id")}

    embedder = EmbeddingService(settings.embedding_model)
    retriever = RetrievalService(embedder, settings.chroma_persist_dir, settings.collection_name)
    rag = RAGService(settings, retriever, LLMService(settings.llm_base_url, None, None), WebSearchService(enabled=False))

    test_queries: list[tuple[str, str, str, str]] = []
    for temple in catalogue:
        temple_id = temple["id"]
        name = temple.get("canonical_name") or (temple.get("names") or [temple_id])[0]
        test_queries.append((temple_id, "temple_name", "present", NAME_QUERY.format(name=name)))
        for category, template in CATEGORY_QUESTIONS.items():
            status = coverage_by_id[temple_id]["categories"][category]["status"]
            test_queries.append((temple_id, category, status, template.format(name=name)))

    # Batch embedding all questions avoids loading/running the encoder 1,500
    # times. Chroma is then queried in small per-temple batches with metadata
    # filters so similarly named temples cannot bleed into each other.
    vectors = embedder.embed_texts([item[3] for item in test_queries])
    rows_by_temple: dict[str, list[dict]] = {}
    cursor = 0
    for temple in catalogue:
        temple_id = temple["id"]
        batch_size = len(CATEGORY_QUESTIONS) + 1
        batch_queries = test_queries[cursor:cursor + batch_size]
        batch_vectors = vectors[cursor:cursor + batch_size]
        cursor += batch_size
        result = retriever.collection.query(
            query_embeddings=batch_vectors,
            n_results=min(5, max(1, retriever.count())),
            where={"temple_id": temple_id},
            include=["documents", "metadatas", "distances"],
        )
        records = []
        for qindex, (query_temple_id, category, expected_status, question) in enumerate(batch_queries):
            ids = (result.get("ids") or [[]])[qindex]
            texts = (result.get("documents") or [[]])[qindex]
            metadatas = (result.get("metadatas") or [[]])[qindex]
            distances = (result.get("distances") or [[]])[qindex]
            hits = []
            for chunk_id, text, metadata, distance in zip(ids, texts, metadatas, distances):
                metadata = metadata or {}
                document_id = metadata.get("document_id")
                expected_source = source_by_doc.get(document_id, {}).get("source_url")
                category_pattern = TOPIC_PATTERNS.get(category)
                relevant_topic = bool(category_pattern and category_pattern.search(text or ""))
                hits.append({
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "temple_id": metadata.get("temple_id"),
                    "topic": metadata.get("topic"),
                    "distance": float(distance),
                    "source_title": metadata.get("source_title"),
                    "source_url": metadata.get("source_url"),
                    "citation_url_matches_document": bool(expected_source) and expected_source == metadata.get("source_url"),
                    "passage_has_category_evidence_terms": relevant_topic,
                    "excerpt": (text or "")[:360],
                    "_full_text_for_topic_filter": text or "",
                })
            expected_docs = set(coverage_by_id[query_temple_id]["categories"].get(category, {}).get("document_ids", [])) if category in TOPIC_PATTERNS else set()
            category_hit = any(hit["document_id"] in expected_docs and hit["passage_has_category_evidence_terms"] for hit in hits)
            relevant_hits = [hit for hit in hits if hit["distance"] <= settings.relevance_threshold]
            if category == "temple_name":
                topic_filtered_hits = relevant_hits
            else:
                rag_chunks = [RetrievedChunk(
                    chunk_id=hit["chunk_id"], text=hit["_full_text_for_topic_filter"], distance=hit["distance"],
                    metadata={
                        "topic": hit.get("topic"), "temple_id": hit.get("temple_id"),
                        "document_id": hit.get("document_id"), "source_url": hit.get("source_url"),
                    },
                ) for hit in relevant_hits]
                retained = {chunk.chunk_id for chunk in rag._filter_to_requested_topics(question, rag_chunks)}
                topic_filtered_hits = [hit for hit in relevant_hits if hit["chunk_id"] in retained]
            unsupported_test = expected_status == "Missing"
            unsupported_leak = unsupported_test and bool(topic_filtered_hits)
            if category == "temple_name":
                success = bool(hits) and all(hit["temple_id"] == query_temple_id for hit in hits)
                outcome = "temple_scoped_passage_retrieved" if success else "no_temple_scoped_passage"
            elif unsupported_test:
                success = not unsupported_leak
                outcome = "no_category_support_in_relevant_hits" if success else "other_relevant_chunk_may_leak_into_answer"
            else:
                success = category_hit
                outcome = "topic_evidence_retrieved" if success else "expected_topic_evidence_not_retrieved"
            records.append({
                "category": category,
                "question": question,
                "coverage_status": expected_status,
                "expected_evidence_document_ids": sorted(expected_docs),
                "retrieved": hits,
                "context_after_topic_filter": [hit["chunk_id"] for hit in topic_filtered_hits],
                "topic_filter_rejected_relevant_hits": len(relevant_hits) - len(topic_filtered_hits),
                "retrieval_success": success,
                "topic_relevance_success": category_hit if category in TOPIC_PATTERNS else None,
                "unsupported_question_test": unsupported_test,
                "potential_unsupported_context": unsupported_leak,
                "citation_urls_match_local_source_documents": all(hit["citation_url_matches_document"] for hit in hits),
                "outcome": outcome,
            })
            for hit in hits:
                hit.pop("_full_text_for_topic_filter", None)
        rows_by_temple[temple_id] = records

    # Ambiguous/similar-name checks are generated from actual catalogue aliases.
    names_by_id = {}
    for temple in catalogue:
        names_by_id[temple["id"]] = temple.get("canonical_name") or (temple.get("names") or [temple["id"]])[0]
    similar_pairs = []
    name_items = list(names_by_id.items())
    for i, (left_id, left_name) in enumerate(name_items):
        for right_id, right_name in name_items[i + 1:]:
            left_norm, right_norm = normalized_name(left_name), normalized_name(right_name)
            if not left_norm or not right_norm:
                continue
            ratio = SequenceMatcher(None, left_norm, right_norm).ratio()
            if ratio >= 0.82:
                similar_pairs.append((ratio, left_id, left_name, right_id, right_name))
    similar_pairs.sort(reverse=True)

    followup_results = []
    for temple in catalogue:
        temple_id = temple["id"]
        history = [
            ConversationMessage(role="user", content="Tell me about this temple."),
            ConversationMessage(role="assistant", content="Here is the temple overview.", context_temple_id=temple_id),
        ]
        resolved = rag._resolve_temple_context(FOLLOWUP_QUESTION, history, None)
        followup_results.append({"temple_id": temple_id, "question": FOLLOWUP_QUESTION, "resolved_temple_id": resolved, "passed": resolved == temple_id})

    summaries = Counter()
    category_summary: dict[str, Counter] = {category: Counter() for category in CATEGORY_QUESTIONS}
    citation_checks = 0
    citation_correct = 0
    unsupported_count = 0
    unsupported_risk_count = 0
    for temple_id, records in rows_by_temple.items():
        for record in records:
            summaries[(record["category"], "tested")] += 1
            summaries[(record["category"], "passed" if record["retrieval_success"] else "failed")] += 1
            if record["category"] in category_summary:
                category_summary[record["category"]][record["outcome"]] += 1
            if record["category"] != "temple_name":
                unsupported_count += int(record["unsupported_question_test"])
                unsupported_risk_count += int(record["potential_unsupported_context"])
            for hit in record["retrieved"]:
                citation_checks += 1
                citation_correct += int(hit["citation_url_matches_document"])

    ambiguous_evaluations = []
    for ratio, left_id, left_name, right_id, right_name in similar_pairs:
        for temple_id, query_name in ((left_id, left_name), (right_id, right_name)):
            query = NAME_QUERY.format(name=query_name)
            resolved_ids = rag._mentioned_temple_ids(query)
            vector = embedder.embed_query(query)
            result = retriever.collection.query(
                query_embeddings=[vector], n_results=5, where={"temple_id": temple_id},
                include=["documents", "metadatas", "distances"],
            )
            returned = [meta.get("temple_id") for meta in (result.get("metadatas") or [[]])[0]]
            ambiguous_evaluations.append({
                "similar_pair": [{"temple_id": left_id, "name": left_name}, {"temple_id": right_id, "name": right_name}],
                "similarity_ratio": ratio,
                "query_temple_id": temple_id,
                "query": query,
                "name_resolved_temple_ids": resolved_ids,
                "name_resolution_passed": resolved_ids == [temple_id],
                "retrieved_temple_ids": returned,
                "metadata_filter_kept_results_scoped": bool(returned) and all(value == temple_id for value in returned),
            })

    output = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "evaluation_mode": "Local ChromaDB retrieval and source-metadata verification; no OpenRouter calls and no live web search.",
        "catalogue_count": len(catalogue),
        "collection_name": settings.collection_name,
        "persist_directory": settings.chroma_persist_dir,
        "collection_chunk_count": retriever.count(),
        "query_count": len(test_queries) + len(ambiguous_evaluations),
        "summary": {
            "temple_name_queries": len(catalogue),
            "temple_name_queries_passed": sum(rows_by_temple[t["id"]][0]["retrieval_success"] for t in catalogue),
            "topic_queries": len(catalogue) * len(CATEGORY_QUESTIONS),
            "topic_query_results_by_category": {key: dict(value) for key, value in category_summary.items()},
            "evidence_available_category_queries": sum(1 for rows in rows_by_temple.values() for row in rows if row["category"] in CATEGORY_QUESTIONS and row["coverage_status"] != "Missing"),
            "evidence_available_category_queries_passed": sum(1 for rows in rows_by_temple.values() for row in rows if row["category"] in CATEGORY_QUESTIONS and row["coverage_status"] != "Missing" and row["retrieval_success"]),
            "unsupported_category_queries": unsupported_count,
            "unsupported_category_queries_with_potential_other_context": unsupported_risk_count,
            "topic_gate_evaluation": "Actual RAG topic filter was applied to locally retrieved relevant hits; this evaluates context admission, not answer correctness.",
            "citation_metadata_checks": citation_checks,
            "citation_metadata_matches": citation_correct,
            "followup_questions": len(followup_results),
            "followup_scope_passed": sum(item["passed"] for item in followup_results),
            "similar_name_pairs_found": len(similar_pairs),
            "similar_name_scope_checks": len(ambiguous_evaluations),
            "similar_name_resolution_passed": sum(item["name_resolution_passed"] for item in ambiguous_evaluations),
            "similar_name_metadata_filter_passed": sum(item["metadata_filter_kept_results_scoped"] for item in ambiguous_evaluations),
            "external_llm_called": False,
        },
        "temples": [
            {"temple_id": temple["id"], "name": names_by_id[temple["id"]], "tests": rows_by_temple[temple["id"]]}
            for temple in catalogue
        ],
        "followup_checks": followup_results,
        "similar_name_checks": ambiguous_evaluations,
        "all_similar_name_pairs_detected": [{"similarity_ratio": ratio, "left_temple_id": left_id, "left_name": left_name, "right_temple_id": right_id, "right_name": right_name} for ratio, left_id, left_name, right_id, right_name in similar_pairs],
        "interpretation": [
            "A topic retrieval passes only when a retrieved passage belongs to a source document identified by the coverage audit and the passage itself contains category terms; a temple-name match alone does not pass.",
            "Unsupported checks detect potential unrelated relevant chunks, not whether a live LLM would refuse or invent. No LLM answer generation was run.",
            "Category evidence is heuristic; citations must still receive human claim-to-source review.",
        ],
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(OUTPUT), "summary": output["summary"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
