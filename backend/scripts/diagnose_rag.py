#!/usr/bin/env python3
"""
Diagnostic script for Temple & Heritage RAG pipeline.
Prints a sanitized report for each test question without exposing secrets.
"""
import json
import sys

from app.config import Settings
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.services.web_search_service import WebSearchService
from app.services.rag_service import RAGService, RAGResult
from app.schemas.chat import Citation


def print_section(title):
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_query(query):
    print(f"\n  Query: {query}")


def print_chunks(chunks, label=""):
    if not chunks:
        print(f"  {label}: (no chunks retrieved)")
        return
    for i, c in enumerate(chunks, 1):
        text_excerpt = c.text[:60].replace("\n", " ")
        meta = c.metadata
        src = meta.get("source_url", "unknown")
        tid = meta.get("temple_id", "unknown")
        print(f"    {i}. id={c.chunk_id}, dist={c.distance:.4f} (cosine, lower=more relevant)")
        print(f"      text: {text_excerpt}...")
        print(f"      src_url: {src}")
        print(f"      temple_id: {tid}")


def print_citations(citations):
    if not citations:
        print("  citations: (none)")
        return
    for c in citations:
        print(f"    - source_id={c.source_id}, source_url={c.source_url}")
        print(f"      excerpt: {c.excerpt[:50] if c.excerpt else 'none'}...")


def main():
    # Initialize services with actual configuration
    settings = Settings()
    svc = EmbeddingService()
    retr = RetrievalService(svc, 'data/chroma', 'temple_heritage')
    llm_api_key = settings.llm_api_key.get_secret_value() if settings.llm_api_key else None
    llm = LLMService(settings.llm_base_url, llm_api_key, settings.llm_model)
    ws = WebSearchService(enabled=False)  # disabled by default per config

    # Print pipeline configuration
    print_section("PIPELINE CONFIGURATION")
    print(f"  Collection name: temple_heritage")
    print(f"  Persistence directory: data/chroma")
    print(f"  Embedding model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    print(f"  Chunk count from ChromaDB: {retr.count()}")
    print(f"  LLM enabled: {llm.is_enabled}")
    print(f"  Web search enabled: {ws.enabled}")
    print()

    # Test questions
    queries = [
        "Who commissioned the Brihadeeswarar Temple?",
        "What is the architectural significance of the Shore Temple?",
        "Describe the Konark Sun Temple.",
        "What is known about the Meenakshi Temple?",
        "What is the significance of Jagannath Rath Yatra?",
        "Compare Dravidian and Kalinga temple architecture.",
        "Ask about a topic absent from the corpus: quantum computing history.",
        "Ask an unrelated question: how to repair a car engine.",
    ]

    for query in queries:
        print_section(f"TEST: {query}")
        print_query(query)

        # 1. Retrieval
        chunks = retr.retrieve(query, top_k=5)
        print_section("  RETRIEVAL RESULTS")
        print(f"  Indexed chunk count: {retr.count()}")
        print_chunks(chunks, "Retrieved chunks")
        passed_threshold = [c for c in chunks if c.distance <= settings.relevance_threshold]
        print(f"  Chunks passing relevance threshold (≤{settings.relevance_threshold}): {len(passed_threshold)}")

        # 2. LLM generation
        print_section("  LLM GENERATION")
        try:
            result = rag.answer_question(query, language='en')
            llm_called = True
            print(f"  LLM called: Yes")
            print(f"  Answer: {result.answer[:80]}...")
            print(f"  insufficient_evidence: {result.insufficient_evidence}")
            print(f"  generation_disabled: {result.generation_disabled}")
            print(f"  Citations: {len(result.citations)}")
            print_citations(result.citations)
            print(f"  Web sources: {len(result.web_sources)}")
            if result.web_sources:
                for ws in result.web_sources:
                    print(f"      web: title={ws.title[:30]}..., url={ws.url}")
        except Exception as e:
            llm_called = False
            print(f"  LLM called: No (error: {type(e).__name__}: {str(e)[:60]})")

        # 3. Final status
        print_section("  FINAL STATUS")
        print(f"  answer: {result.answer[:80]}..." if len(result.answer) > 80 else f"  answer: {result.answer}")
        print(f"  insufficient_evidence: {result.insufficient_evidence}")
        print(f"  generation_disabled: {result.generation_disabled}")
        print(f"  citations: {len(result.citations)}")
        print_citations(result.citations)
        if result.web_sources:
            print(f"  web_sources: {len(result.web_sources)} sources from search")

    print_section("DIAGNOSTIC COMPLETE")


if __name__ == '__main__':
    main()