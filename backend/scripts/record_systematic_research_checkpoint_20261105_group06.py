"""Record inspected state-government details for the Chhatrari Shakti temple."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TODAY = "2026-11-05"


def main() -> None:
    cat_path = DATA / "catalogue.json"
    docs_path = DATA / "raw" / "temple_sources.json"
    plan_path = DATA / "research_plan_all_217.json"
    cat = json.loads(cat_path.read_text(encoding="utf-8"))
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    temple_id = "asi_himachal_pra_29892a543f8e7863"
    temple = next(t for t in cat if t["id"] == temple_id)
    doc_id = "systematic_research_20261105_chhatrari_shakti_devi_state_architecture"
    if doc_id not in {d.get("document_id") for d in docs}:
        body = (
            "The Government of Himachal Pradesh's Hindu pilgrimage page identifies Chattari Temple near Bharmaur in Chamba and reports early examples of carved wood and an 8th-century brass image of Shakti there. "
            "This provides a state-government description of the temple's woodwork and a dated metal image, but the inspected passage does not identify the image's maker, explain the dating basis, name a donor or inscription, or give a detailed account of the temple's construction. "
            "The source's broad description is retained as its account pending human review; it is not treated as an independently established date for the whole temple. Accessed 2026-11-05."
        )
        docs.append({
            "document_id": doc_id, "temple_id": temple_id,
            "temple_name": temple.get("canonical_name"), "state": temple.get("state"),
            "district": temple.get("district"), "topic": "architecture_history_religious_cultural_significance",
            "title": "Shakti Devi Temple, Chhatrari: state account of carved wood and a brass image",
            "source_title": "Hindu Pilgrimage", "source_url": "https://himachal.nic.in/Content/HtmlPage?qs=LdEF+AuYkB4Dve235DK9HQ%3D%3D",
            "publisher": "Government of Himachal Pradesh", "source_type": "official_state_government_page",
            "language": "en", "publication_date": None, "retrieval_date": TODAY,
            "collection_timestamp": datetime.now(timezone.utc).isoformat(),
            "content_hash": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "verification_status": "source_review_pending", "review_status": "pending_human_review",
            "is_paraphrase": True, "text": body,
        })
        refs = temple.setdefault("document_ids", [])
        if doc_id not in refs:
            refs.append(doc_id)
    checks = plan.setdefault("source_checks_this_operation", [])
    checks.append({
        "source_title": "Hindu Pilgrimage",
        "source_url": "https://himachal.nic.in/Content/HtmlPage?qs=LdEF+AuYkB4Dve235DK9HQ%3D%3D",
        "publisher": "Government of Himachal Pradesh", "source_type": "official_state_government_page",
        "publication_date": None, "accessed_date": TODAY, "linked_temple_ids": [temple_id],
        "categories_with_relevant_source_content": ["architecture", "history", "religious_cultural_significance"],
        "inspection_method": "Opened and read the Chattari Temple paragraph in the state page.",
        "note": "Catalogued locality Chhatrari matches the source's Chattari entry. The dated image claim is attributed to the government page and remains pending review.",
    })
    unique = {}
    for check in checks:
        unique[(check.get("source_url"), tuple(sorted(check.get("linked_temple_ids", []))))] = check
    plan["source_checks_this_operation"] = list(unique.values())
    plan["last_checkpoint"] = {
        "checkpoint_id": "systematic_research_20261105_himachal_group_06",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "temple_ids": [temple_id], "documents_added": [doc_id],
        "note": "Inspected official state pilgrimage page; document remains pending human source review.",
    }
    cat_path.write_text(json.dumps(cat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    docs_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"catalogue": len(cat), "documents": len(docs), "document_id": doc_id}, indent=2))


if __name__ == "__main__":
    main()
