"""Record source-inspected ASI Guwahati Circle temple evidence."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
ACCESS_DATE = "2026-11-05"
COLLECTED_AT = datetime.now(timezone.utc).isoformat()
PROFILE_PUBLISHER = "Archaeological Survey of India, Guwahati Circle"
ACTIVITIES_URL = "https://asiguwahaticircle.gov.in/paw.pdf"

ITEMS = [
    {
        "temple_id": "asi_assam_24dc8f3855351f21",
        "slug": "dhandi_asi_profile_history_architecture",
        "title": "Dhandi Temple: ASI profile on period, form, and earthquake damage",
        "source_title": "Dhandi Temple, N.C. Kamadayal (Gohpur Mouza)",
        "url": "https://asiguwahaticircle.gov.in/dhandi.html",
        "topic": "history_architecture_heritage_conservation",
        "categories": ["historical_background", "architecture", "heritage_conservation"],
        "text": "The Archaeological Survey of India (ASI), Guwahati Circle profile describes the remains of Dhandi Temple at N.C. Kamadayal, Gohpur Mouza, as attributable to the Ahom kings and dating to the 18th century CE. It describes an octagonal temple plan on a raised platform and says the temple was damaged in the 1897 earthquake. The page labels the district Sonitpur, while the present catalogue uses Biswanath district and Dhandi (Gohpur) locality; this administrative naming difference is retained for review. The profile does not identify a presiding deity or provide a festival calendar or current visitor details. Accessed 5 November 2026.",
    },
    {
        "temple_id": "asi_assam_24dc8f3855351f21",
        "slug": "dhandi_asi_2010_11_conservation_report",
        "title": "Dhandi Temple: ASI report of 2010–11 conservation work",
        "source_title": "Activities of Archaeological Survey of India, Guwahati Circle during 2010 & 2011",
        "url": ACTIVITIES_URL,
        "topic": "heritage_conservation_architecture",
        "categories": ["architecture", "heritage_conservation"],
        "text": "The Archaeological Survey of India (ASI), Guwahati Circle report covering activities during 2010–2011 describes Dhandi Temple at N.C. Kamdayal, then identified as Sonitpur district, as octagonal brick ruins attributed to the Ahom period and damaged in the 1897 earthquake. The report records restoration of the surviving ancient brick structure using lime-surkhi mortar and construction of a brick-on-edge pathway extending to the fallen upper part. These are works reported for 2010–2011; the document does not establish the monument's present condition or later conservation. Accessed 5 November 2026; source section inspected at extracted PDF lines 179–192.",
    },
    {
        "temple_id": "asi_assam_641483ffa47752ae",
        "slug": "khaspur_ranachandi_asi_architecture_cachari_history",
        "title": "Temple of Ranachandi at Khaspur: ASI profile",
        "source_title": "The Temple of Ranachandi",
        "url": "https://www.asiguwahaticircle.gov.in/ranachandi.html",
        "topic": "history_architecture_religious_cultural_significance",
        "categories": ["historical_background", "architecture", "religious_cultural_significance"],
        "text": "The Archaeological Survey of India (ASI), Guwahati Circle identifies the Temple of Ranachandi as a brick-masonry temple dedicated to goddess Ranachandi and attributes its construction to Cachari rulers in the late medieval period. The profile describes a rectangular sanctum measuring 5.50 by 2.80 metres, a single western doorway, and a chala roof that it says shows the influence of Bengal architecture. The page does not give a precise construction year, identify inscriptions, or state festival or current visitor information. Accessed 5 November 2026.",
    },
    {
        "temple_id": "asi_assam_6bca1547cfa3d7cc",
        "slug": "hajo_kedar_asi_inscription_architecture",
        "title": "Shri Shri Kedar Temple, Hajo: ASI profile on shrine and inscription",
        "source_title": "Shri Shri Kedar Temple, Hajo",
        "url": "https://asiguwahaticircle.gov.in/kedar%20temple.html",
        "topic": "history_architecture_religious_cultural_significance_inscriptions_historical_evidence",
        "categories": ["historical_background", "architecture", "religious_cultural_significance", "inscriptions_historical_evidence"],
        "text": "The Archaeological Survey of India (ASI), Guwahati Circle profile identifies Shri Shri Kedar Temple at Hajo as enshrining a Siva-linga in its central chamber. It describes a garbhagriha and a small mukhamandapa. The page says an inscription attached to the temple shows that Ahom king Rajeswara Singha (1751–1769 CE) erected two masonry walls along it; this is evidence for that documented work, not a stated original construction date. The profile's heading and bus-stand reference identify Hajo, though its locality field also says Guwahati; that source wording is preserved for review. It does not provide a festival calendar or current visitor guidance. Accessed 5 November 2026.",
    },
    {
        "temple_id": "asi_assam_6bca1547cfa3d7cc",
        "slug": "hajo_kedar_asi_2010_11_conservation_report",
        "title": "Shri Shri Kedar Temple, Hajo: ASI report of 2010–11 conservation work",
        "source_title": "Activities of Archaeological Survey of India, Guwahati Circle during 2010 & 2011",
        "url": ACTIVITIES_URL,
        "topic": "heritage_conservation",
        "categories": ["heritage_conservation"],
        "text": "The Archaeological Survey of India (ASI), Guwahati Circle report covering activities during 2010–2011 identifies Shri Shri Kedar Temple at Hajo, Kamrup. It records a retaining wall on the western side and an apron over a PCC bed intended to reduce soil erosion and water percolation near the foundation. This is a dated account of conservation measures reported in 2010–2011; it does not establish whether those measures remain intact or describe current site condition. Accessed 5 November 2026; source section inspected at extracted PDF lines 245–260.",
    },
    {
        "temple_id": "asi_assam_73c2196bfdf2df7a",
        "slug": "hajo_kameshwar_asi_2010_11_architecture_conservation",
        "title": "Shri Shri Kameshwar Temple, Hajo: ASI report on architecture and conservation",
        "source_title": "Activities of Archaeological Survey of India, Guwahati Circle during 2010 & 2011",
        "url": ACTIVITIES_URL,
        "topic": "history_architecture_religious_cultural_significance_heritage_conservation",
        "categories": ["historical_background", "architecture", "religious_cultural_significance", "heritage_conservation"],
        "text": "The Archaeological Survey of India (ASI), Guwahati Circle report covering activities during 2010–2011 describes Shri Shri Kameshwar Temple at Hajo as standing on Mandachala hillock and enshrining a Sivalinga. It identifies brick masonry, a domical sikhara and four corner towers, and assigns the temple to the late medieval period without a narrower date. The report says soil erosion risk on the hillock had been addressed by providing a stone retaining wall on the southern side; this is a historical report of work, not a statement of present condition. It also mentions tree rounds provided for visitors to sit, but does not give current visitor rules, hours or fees. Accessed 5 November 2026; source section inspected at extracted PDF lines 227–244.",
    },
]


def main() -> None:
    docs_path = DATA / "raw" / "temple_sources.json"
    catalogue_path = DATA / "catalogue.json"
    plan_path = DATA / "research_plan_all_217.json"
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    catalog_by_id = {row["id"]: row for row in catalogue}
    plan_by_id = {row["temple_id"]: row for row in plan["temples"]}
    existing_ids = {doc.get("document_id") for doc in docs}
    added = []
    for item in ITEMS:
        temple = catalog_by_id[item["temple_id"]]
        doc_id = f"systematic_research_20261105_{item['slug']}"
        text = " ".join(item["text"].split())
        publisher = PROFILE_PUBLISHER
        doc = {
            "document_id": doc_id,
            "temple_id": temple["id"],
            "temple_name": temple["canonical_name"],
            "state": temple["state"],
            "district": temple["district"],
            "topic": item["topic"],
            "title": item["title"],
            "source_title": item["source_title"],
            "source_url": item["url"],
            "publisher": publisher,
            "source_type": "official_asi_circle_temple_profile" if item["url"] != ACTIVITIES_URL else "official_asi_circle_conservation_report",
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
        if doc_id not in existing_ids:
            docs.append(doc)
            added.append(doc)
        if doc_id not in temple.setdefault("document_ids", []):
            temple["document_ids"].append(doc_id)
        row = plan_by_id[item["temple_id"]]
        for field in ("sources_inspected", "previously_inspected_source_urls"):
            if item["url"] not in row.setdefault(field, []):
                row[field].append(item["url"])
        row["research_status"] = "enriched"
        row["last_completed_checkpoint"] = "2026-11-05-group13"
        row["page_evidence_categories"] = sorted(set(row.get("page_evidence_categories", [])) | set(item["categories"]))
        notes = row.setdefault("research_notes", [])
        if isinstance(notes, str):
            notes = [notes] if notes else []
            row["research_notes"] = notes
        note = "ASI Guwahati Circle temple page and/or dated 2010–2011 activity report inspected; historic report claims are distinguished from current condition."
        if note not in notes:
            notes.append(note)
    checks = plan.setdefault("source_checks_this_operation", [])
    source_groups = {}
    for item in ITEMS:
        source_groups.setdefault(item["url"], []).append(item)
    for url, items in source_groups.items():
        report = url == ACTIVITIES_URL
        check = {
            "source_title": "Activities of Archaeological Survey of India, Guwahati Circle during 2010 & 2011" if report else "; ".join(i["source_title"] for i in items),
            "source_url": url,
            "publisher": PROFILE_PUBLISHER,
            "source_type": "official_asi_circle_conservation_report" if report else "official_asi_circle_temple_profile",
            "publication_date": None,
            "accessed_date": ACCESS_DATE,
            "linked_temple_ids": sorted({i["temple_id"] for i in items}),
            "categories_with_relevant_source_content": sorted({cat for i in items for cat in i["categories"]}),
            "inspection_method": "Opened the ASI Guwahati Circle HTML temple profile or actual activity-report PDF and read the named temple section.",
            "note": "PDF describes work undertaken in 2010–2011 and is not treated as evidence of current condition. No automated collection was run.",
        }
        if not any(c.get("source_url") == url and set(check["linked_temple_ids"]).issubset(set(c.get("linked_temple_ids", []))) for c in checks):
            checks.append(check)
    docs_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    catalogue_path.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"catalogue": len(catalogue), "documents": len(docs), "added": [d["document_id"] for d in added]}, indent=2))


if __name__ == "__main__":
    main()
