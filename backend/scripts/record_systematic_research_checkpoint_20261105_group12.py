"""Record two manually inspected ASI Guwahati Circle temple profiles."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
ACCESS_DATE = "2026-11-05"
COLLECTED_AT = datetime.now(timezone.utc).isoformat()
ITEMS = [
    {
        "temple_id": "asi_assam_4bf398fbc498bf4d",
        "url": "https://asiguwahaticircle.gov.in/bordol.html",
        "source_title": "Bordol Temple (Biswanath), ASI Guwahati Circle profile",
        "slug": "biswanath_bordol_asi_circle_architecture_patronage",
        "topic": "history_architecture_religious_cultural_significance",
        "categories": ["historical_background", "architecture", "religious_cultural_significance"],
        "text": "The Archaeological Survey of India (ASI), Guwahati Circle describes Bordol Temple at Bishwanath as a brick-built Shiva temple on the north bank of the Brahmaputra. Its profile describes a sanctum with a domical shikhara clustered by anga-shikharas, and a porch with a low do-chala roof compared with an Assamese hut form. The page says the temple is believed to have been built by Ahom king Rajesvar Singha, whose reign it gives as 1751–1769 CE; it does not provide a more precise construction year. The ASI profile labels the district Sonitpur and locality Bishwanath, while the present catalogue record uses Biswanath district and Biswanathghat locality; this place-name difference is retained for review. The page gives no temple-specific festival schedule, inscriptions or current visitor timings. Accessed 5 November 2026.",
    },
    {
        "temple_id": "asi_assam_08eedbf158fc288a",
        "url": "https://www.asiguwahaticircle.gov.in/ganesh%20temple.html",
        "source_title": "Shri Shri Ganesh Temple, Hajo, ASI Guwahati Circle profile",
        "slug": "hajo_shri_shri_ganesh_asi_circle_history_architecture",
        "topic": "history_architecture_religious_cultural_significance",
        "categories": ["historical_background", "architecture", "religious_cultural_significance"],
        "text": "The Archaeological Survey of India (ASI), Guwahati Circle profile for Shri Shri Ganesh Temple in Hajo says the temple is believed to date to 1744 CE, during the reign of Ahom king Pramatta Singha. It describes an elephant-shaped Ganesha image in a square garbhagriha, with a rectangular mukhamandapa; low sunken niches on the sanctum's exterior; a domical shikhara; and a barrel-vaulted roof over the mukhamandapa. The wording is the ASI profile's account and is not an independent inscriptional date. The page does not discuss the temple's festivals, conservation history or current visitor hours and fees. Accessed 5 November 2026.",
    },
]


def main() -> None:
    docs_path = DATA / "raw" / "temple_sources.json"
    catalogue_path = DATA / "catalogue.json"
    plan_path = DATA / "research_plan_all_217.json"
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    catalog_by_id = {item["id"]: item for item in catalogue}
    plan_by_id = {item["temple_id"]: item for item in plan["temples"]}
    existing = {doc.get("document_id") for doc in docs}
    added = []
    for item in ITEMS:
        temple = catalog_by_id[item["temple_id"]]
        doc_id = f"systematic_research_20261105_{item['slug']}"
        text = " ".join(item["text"].split())
        doc = {
            "document_id": doc_id,
            "temple_id": temple["id"],
            "temple_name": temple["canonical_name"],
            "state": temple["state"],
            "district": temple["district"],
            "topic": item["topic"],
            "title": item["source_title"],
            "source_title": item["source_title"],
            "source_url": item["url"],
            "publisher": "Archaeological Survey of India, Guwahati Circle",
            "source_type": "official_asi_circle_temple_profile",
            "language": "en",
            "publication_date": None,
            "retrieval_date": ACCESS_DATE,
            "collection_timestamp": COLLECTED_AT,
            "content_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "verification_status": "source_review_pending",
            "review_status": "pending_human_review",
            "is_paraphrase": True,
            "text": text,
        }
        if doc_id not in existing:
            docs.append(doc)
            added.append(doc)
        if doc_id not in temple.setdefault("document_ids", []):
            temple["document_ids"].append(doc_id)
        row = plan_by_id[item["temple_id"]]
        for field in ("sources_inspected", "previously_inspected_source_urls"):
            if item["url"] not in row.setdefault(field, []):
                row[field].append(item["url"])
        row["research_status"] = "enriched"
        row["last_completed_checkpoint"] = "2026-11-05-group12"
        row["page_evidence_categories"] = sorted(set(row.get("page_evidence_categories", [])) | set(item["categories"]))
        notes = row.setdefault("research_notes", [])
        if isinstance(notes, str):
            notes = [notes] if notes else []
            row["research_notes"] = notes
        note = "ASI Guwahati Circle's named temple page was opened and read; the source's qualified claims and locality wording were retained."
        if note not in notes:
            notes.append(note)
        row["remaining_gaps"] = sorted(set(row.get("remaining_gaps", [])) | {"festivals_traditions", "inscriptions_historical_evidence", "heritage_conservation", "visitor_information"})
    checks = plan.setdefault("source_checks_this_operation", [])
    for item in ITEMS:
        check = {
            "source_title": item["source_title"],
            "source_url": item["url"],
            "publisher": "Archaeological Survey of India, Guwahati Circle",
            "source_type": "official_asi_circle_temple_profile",
            "publication_date": None,
            "accessed_date": ACCESS_DATE,
            "linked_temple_ids": [item["temple_id"]],
            "categories_with_relevant_source_content": item["categories"],
            "inspection_method": "Opened the ASI Guwahati Circle page and read the named temple profile in full.",
            "note": "No search snippet was used as source evidence; the page's belief-qualified date language was preserved.",
        }
        if not any(c.get("source_url") == item["url"] and item["temple_id"] in c.get("linked_temple_ids", []) for c in checks):
            checks.append(check)
    docs_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    catalogue_path.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"catalogue": len(catalogue), "documents": len(docs), "added": [d["document_id"] for d in added]}, indent=2))


if __name__ == "__main__":
    main()
