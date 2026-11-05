"""Check Batch 4 retrieval scope, source provenance, and follow-up behavior.

Uses the persistent ChromaDB collection and local embeddings, but deliberately
disables external LLM and web search so this report tests evidence retrieval,
not generated-answer quality or upstream availability.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.config import Settings
from app.schemas.chat import ConversationMessage
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.retrieval_service import RetrievalService
from app.services.web_search_service import WebSearchService

DATA = BACKEND / "data"
MANIFEST_PATH = DATA / "enrichment_manifest_batch_04.json"
CORPUS_PATH = DATA / "raw" / "temple_sources.json"
REPORT_PATH = DATA / "enrichment_evaluation_batch_04.json"

PRIMARY_CASES = [
    ("konark", "How is the Sun Temple at Konark structured as Surya's chariot?", "architecture_chariot_plan"),
    ("konark", "Which festival does UNESCO associate with living cultural practices at Konark?", "sculpture_iconography"),
    ("asi_telangana_f3a7458053e48f24", "What materials and floating bricks are used in Ramappa's vimana?", "architecture_engineering"),
    ("asi_karnataka_7c32bc783d1664dc", "Who commissioned Virupaksha Temple at Pattadakal and why?", "history_chalukya_context"),
    ("whc_b5eaf9ee03e0215d1573", "What does the report say about the Balakrishna image at Krishna Temple?", "history_krishnadevaraya"),
    ("whc_5a482f12eb769406674c", "What conservation work was documented at Pattabhirama in 2003?", "conservation_2003"),
    ("whc_0550440746a0ab1b40e6", "What temple plan types occur at Hemakuta and when is Prasanna Virupaksha dated?", "architecture_temple_types"),
    ("asi_gujarat_fd7e0734b68a92df", "Describe the shrine, assembly hall and sacred tank at Modhera.", "architecture_ensemble"),
    ("asi_tamil_nadu_e53edf8ca8494828", "What are the three levels of Vaikuntaperumal's shrine?", "architecture_three_levels"),
    ("asi_himachal_pra_d0cbd9e9b4b403a2", "What do Baijnath's inscriptions say about the temple's foundation?", "history_inscriptions"),
    ("asi_jammu_and_ka_1f8a290d8729fbea", "Describe Martand's courtyard and shrine plan.", "architecture_plan_sculpture"),
]


def main() -> None:
    settings = Settings()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    source_by_id = {doc["document_id"]: doc for doc in corpus}
    expected_docs = [
        source_by_id[doc_id]
        for temple in manifest["temples"]
        for doc_id in temple["document_ids"]
    ]
    embedder = EmbeddingService(settings.embedding_model)
    retrieval = RetrievalService(embedder, settings.chroma_persist_dir, settings.collection_name)
    rag = RAGService(
        settings,
        retrieval,
        LLMService(settings.llm_base_url, None, None),
        WebSearchService(enabled=False),
    )

    document_checks = []
    for doc in expected_docs:
        query = f"{doc['temple_name']} {doc['title']} {doc['topic']}"
        hits = retrieval.retrieve(query, top_k=5, temple_id=doc["temple_id"])
        doc_hits = [hit for hit in hits if hit.metadata.get("document_id") == doc["document_id"]]
        correct_urls = [hit.metadata.get("source_url") == doc["source_url"] for hit in doc_hits]
        document_checks.append({
            "temple_id": doc["temple_id"],
            "document_id": doc["document_id"],
            "topic": doc["topic"],
            "query": query,
            "retrieved_document_ids": [hit.metadata.get("document_id") for hit in hits],
            "retrieved_source_urls": [hit.metadata.get("source_url") for hit in hits],
            "expected_document_retrieved": bool(doc_hits),
            "citation_url_matches_source_record": bool(doc_hits) and all(correct_urls),
            "distances": [hit.distance for hit in doc_hits],
        })

    question_checks = []
    for temple_id, question, expected_topic in PRIMARY_CASES:
        chunks = retrieval.retrieve(question, top_k=5, temple_id=temple_id)
        relevant = [chunk for chunk in chunks if chunk.distance <= settings.relevance_threshold]
        expected = [chunk for chunk in relevant if chunk.metadata.get("topic") == expected_topic]
        result = rag.answer_question(question, temple_id=temple_id)
        citation_sources = {doc["document_id"]: doc["source_url"] for doc in source_by_id.values()}
        citation_matches = all(
            citation_sources.get(cite.source_id) == cite.source_url
            for cite in result.citations
            if cite.source_id in citation_sources
        )
        question_checks.append({
            "temple_id": temple_id,
            "question": question,
            "expected_topic": expected_topic,
            "retrieved_document_ids": [chunk.metadata.get("document_id") for chunk in chunks],
            "relevant_document_ids": [chunk.metadata.get("document_id") for chunk in relevant],
            "expected_topic_retrieved": bool(expected),
            "retrieval_only_citation_urls_match_documents": citation_matches,
            "citation_urls": [cite.source_url for cite in result.citations],
            "llm_generation_disabled": result.generation_disabled,
        })

    # Follow-up resolution is tested through RAGService with the prior assistant
    # context token. This exercises the actual context resolver and temple filter.
    followup_question = "What about the construction date and its layout?"
    followup = rag.answer_question(
        followup_question,
        history=[
            ConversationMessage(role="user", content="Tell me about Pattabhirama Temple at Hampi."),
            ConversationMessage(role="assistant", content="I found information about Pattabhirama Temple.", context_temple_id="whc_5a482f12eb769406674c"),
        ],
    )
    followup = {
        "question": followup_question,
        "resolved_temple_id": followup.context_temple_id,
        "retrieved_document_ids": [chunk.metadata.get("document_id") for chunk in followup.retrieved_chunks],
        "citation_urls": [citation.source_url for citation in followup.citations],
        "correct_temple_scope": followup.context_temple_id == "whc_5a482f12eb769406674c" and all(
            chunk.metadata.get("temple_id") == "whc_5a482f12eb769406674c" for chunk in followup.retrieved_chunks
        ),
    }

    absent_question = "What are Martand's exact opening hours and admission fee today?"
    absent = rag.answer_question(absent_question, temple_id="asi_jammu_and_ka_1f8a290d8729fbea")
    absent_evidence_text = " ".join(chunk.text.casefold() for chunk in absent.retrieved_chunks)
    absent = {
        "question": absent_question,
        "retrieved_document_ids": [chunk.metadata.get("document_id") for chunk in absent.retrieved_chunks],
        "answer": absent.answer,
        "insufficient_evidence": absent.insufficient_evidence,
        "generation_disabled": absent.generation_disabled,
        "evidence_contains_exact_hours_or_fee": any(term in absent_evidence_text for term in ("opens at", "opening hours are", "admission fee is", "ticket costs")),
        "interpretation": "Retrieval-only run; the explicit absence of current hours or fees can be checked in the source wording, but external LLM synthesis was not called.",
    }

    checks = {
        "documents_retrievable": sum(item["expected_document_retrieved"] for item in document_checks),
        "documents_total": len(document_checks),
        "citation_metadata_matches": sum(item["citation_url_matches_source_record"] for item in document_checks),
        "primary_questions_expected_topic_retrieved": sum(item["expected_topic_retrieved"] for item in question_checks),
        "primary_questions_total": len(question_checks),
        "followup_scope_passed": followup["correct_temple_scope"],
        "external_llm_called": False,
        "collection_count": retrieval.count(),
    }
    report = {
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "batch_id": manifest["batch_id"],
        "evaluation_mode": "local retrieval and citation metadata only; no external LLM and no web search",
        "checks": checks,
        "document_checks": document_checks,
        "topic_question_checks": question_checks,
        "followup_check": followup,
        "unsupported_information_check": absent,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"checks": checks, "followup": followup, "unsupported": absent}, ensure_ascii=False, indent=2))

    if checks["documents_retrievable"] != checks["documents_total"]:
        raise SystemExit("One or more Batch 4 documents were not retrieved by their topic query")
    if checks["citation_metadata_matches"] != checks["documents_total"]:
        raise SystemExit("One or more indexed citation URLs do not match the source document")
    if checks["primary_questions_expected_topic_retrieved"] != checks["primary_questions_total"]:
        raise SystemExit("One or more topic questions did not retrieve expected topic evidence")
    if not followup["correct_temple_scope"]:
        raise SystemExit("Follow-up did not remain within the previously identified temple")


if __name__ == "__main__":
    main()
