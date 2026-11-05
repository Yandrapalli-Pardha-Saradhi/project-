"""Run filtered retrieval checks for Batch 3 and record cited source metadata."""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import Settings
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MANIFEST = DATA / "enrichment_manifest_batch_03.json"
DOCS = DATA / "raw" / "temple_sources.json"
OUTPUT = DATA / "enrichment_evaluation_batch_03.json"

QUESTIONS = {
    "whc_b64d0b1bb2989639c1f1": [
        ("How does UNESCO describe the Mahabodhi temple's architecture?", "enrich_batch03_whc_b64d0b1bb2989639c1f1_architecture"),
        ("What is Mahabodhi's historical significance for Buddhism?", "enrich_batch03_whc_b64d0b1bb2989639c1f1_history_religious_significance"),
    ],
    "whc_798b3d431ca45563a0f8": [
        ("What characterizes Khajuraho's Nagara temple architecture?", "enrich_batch03_whc_798b3d431ca45563a0f8_history_architecture"),
        ("What subjects appear in Khajuraho's sculptures and who manages the heritage property?", "enrich_batch03_whc_798b3d431ca45563a0f8_sculpture_heritage_management"),
    ],
    "whc_ffb69144fee941fb01a9": [
        ("How did the Virupaksha temple at Hampi develop and what is its plan?", "enrich_batch03_whc_ffb69144fee941fb01a9_history_architecture_religion"),
    ],
    "whc_0601b84399076df5f6eb": [
        ("What structures are in Hampi's Vitthala temple complex?", "enrich_batch03_whc_0601b84399076df5f6eb_history_architecture"),
        ("What does the 2003 report say about Vitthala temple conservation?", "enrich_batch03_whc_0601b84399076df5f6eb_sculpture_conservation"),
    ],
    "whc_57e81c99363e3334087c": [
        ("Who commissioned Achyutaraya temple and what does its inscription say about the bazaar?", "enrich_batch03_whc_57e81c99363e3334087c_history_architecture_urban_context"),
    ],
    "asi_tamil_nadu_9b2980bb768b7c42": [
        ("Who built the Brihadisvara temple at Gangaikondacholapuram?", "enrich_batch03_asi_tamil_nadu_9b2980bb768b7c42_history_architecture_heritage"),
    ],
    "brihadeeswarar": [
        ("How does UNESCO characterize the architecture of Brihadisvara at Thanjavur?", "enrich_batch03_brihadeeswarar_architecture_heritage"),
    ],
    "shore": [
        ("How does Shore Temple fit into Pallava architecture at Mahabalipuram?", "enrich_batch03_shore_history_architecture_heritage"),
    ],
    "meenakshi": [
        ("What does the district source say about Meenakshi temple architecture and history?", "enrich_batch03_meenakshi_history_architecture_religion"),
        ("Which festivals does Madurai district associate with the Meenakshi temple traditions?", "enrich_batch03_meenakshi_festivals_traditions"),
    ],
    "kashi_vishwanath": [
        ("What is Kashi Vishvanath's religious significance according to the Varanasi district page?", "enrich_batch03_kashi_vishwanath_deity_religious_significance"),
    ],
}


def main() -> None:
    settings = Settings()
    service = RetrievalService(EmbeddingService(settings.embedding_model), settings.chroma_persist_dir, settings.collection_name)
    docs = {row["document_id"]: row for row in json.loads(DOCS.read_text(encoding="utf-8"))}
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = []
    for temple_id, questions in QUESTIONS.items():
        for question, expected_doc_id in questions:
            hits = service.retrieve(question, top_k=10, temple_id=temple_id)
            ids = [hit.metadata.get("document_id") for hit in hits]
            expected = docs[expected_doc_id]
            matching = next((hit for hit in hits if hit.metadata.get("document_id") == expected_doc_id), None)
            rows.append({
                "temple_id": temple_id,
                "question": question,
                "retrieved_document_ids": ids,
                "expected_document_id": expected_doc_id,
                "expected_document_retrieved": matching is not None,
                "expected_distance": matching.distance if matching else None,
                "expected_citation_url": expected["source_url"] if matching else None,
                "citation_url_matches_source_document": bool(matching and matching.metadata.get("source_url") == expected["source_url"]),
                "evidence_source_title": expected["source_title"] if matching else None,
                "evidence_scope": expected["topic"],
                "evidence_review_status": expected["review_status"],
                "answerability": "supported at the scope stated in the source; human review remains required" if matching else "not retrieved; investigate before answering",
            })
    unsupported_question = "Which annual festivals are documented for the Mahabodhi Temple?"
    unsupported_hits = service.retrieve(
        unsupported_question, top_k=10, temple_id="whc_b64d0b1bb2989639c1f1"
    )
    festival_terms = re.compile(r"\b(festival|festivals|annual celebration|procession|ritual schedule)\b", re.I)
    unsupported_rows = [{
        "question": unsupported_question,
        "temple_id": "whc_b64d0b1bb2989639c1f1",
        "retrieved_document_ids": [hit.metadata.get("document_id") for hit in unsupported_hits],
        "retrieved_source_urls": list(dict.fromkeys(hit.metadata.get("source_url") for hit in unsupported_hits if hit.metadata.get("source_url"))),
        "retrieved_text_contains_festival_evidence": any(festival_terms.search(hit.text) for hit in unsupported_hits),
        "expected_behavior": "Briefly state that the indexed sources do not document festivals; do not infer or fabricate a festival.",
        "result": "no_festival_evidence_in_retrieved_text" if not any(festival_terms.search(hit.text) for hit in unsupported_hits) else "manual_review_required",
    }]
    expected_total = sum(len(row["document_ids"]) for row in manifest["temples"])
    new_ids = {doc_id for row in manifest["temples"] for doc_id in row["document_ids"]}
    indexed_new_ids: set[str] = set()
    offset = 0
    total = service.collection.count()
    while offset < total:
        page = service.collection.get(limit=500, offset=offset, include=["metadatas"])
        indexed_new_ids.update(
            metadata.get("document_id") for metadata in page.get("metadatas", [])
            if isinstance(metadata, dict) and metadata.get("document_id") in new_ids
        )
        offset += len(page.get("ids", []))
        if not page.get("ids"):
            break
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "collection": settings.collection_name,
        "indexed_chunk_count": total,
        "new_manifest_document_count": expected_total,
        "new_document_ids_found_in_index": len(indexed_new_ids),
        "retrieval_checks": rows,
        "retrieval_checks_passed": sum(row["expected_document_retrieved"] and row["citation_url_matches_source_document"] for row in rows),
        "retrieval_checks_total": len(rows),
        "unsupported_detail_checks": unsupported_rows,
        "limitations": [
            "Checks exercise vector retrieval and source metadata only; no external LLM generation was called.",
            "Retrieved passages remain pending human review, so successful retrieval is not factual verification.",
        ],
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("indexed_chunk_count", "new_manifest_document_count", "new_document_ids_found_in_index", "retrieval_checks_passed", "retrieval_checks_total")}, ensure_ascii=False, indent=2))
    for row in rows:
        print(json.dumps({key: row[key] for key in ("temple_id", "question", "expected_document_id", "retrieved_document_ids", "expected_document_retrieved", "citation_url_matches_source_document")}, ensure_ascii=False))
    if len(indexed_new_ids) != expected_total or report["retrieval_checks_passed"] != len(rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
