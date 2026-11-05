"""Add researched evidence for two existing Himachal Pradesh temple records."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
CHECKED = "2026-11-05"
ITEMS = [
    {
        "temple_id": "asi_himachal_pra_f2a74ffbd1613f95",
        "document_id": "systematic_research_20261105_champavati_tourism_history",
        "title": "Champavati Temple, Chamba: state tourism account of royal patronage and tradition",
        "topic": "historical_background_religious_cultural_significance",
        "url": "https://tourism.gov.in/sites/default/files/2020-04/Himachal.pdf",
        "source_title": "Final Report on Perspective Plan for Tourism in Himachal Pradesh",
        "publisher": "Ministry of Tourism, Government of India; report prepared by Drishti Strategic Research Services",
        "source_type": "government_tourism_planning_report",
        "publication_date": None,
        "page_ref": "Chapter 3, printed page 33; PDF text lines 4342–4343",
        "categories": ["historical_background", "religious_cultural_significance"],
        "text": "The Ministry of Tourism-hosted Himachal Pradesh tourism perspective-plan report locates Champavati Temple behind the City Police Post and Treasury building in Chamba. It attributes the temple's construction to Raja Sahil Varman and says it was built in memory of his daughter Champavati. The report phrases the daughter's role in persuading her father to establish Chamba at its present location as a belief, not as a separately established historical fact. The passage provides no architectural description, deity identification, festival calendar, inscriptions, conservation account or current visitor timings. The separate National Mission on Monuments and Antiquities detail page could not be fetched during this research and was not used for claims. Accessed 5 November 2026.",
    },
    {
        "temple_id": "asi_himachal_pra_14fdecc910252f5f",
        "document_id": "systematic_research_20261105_panchvaktra_asi_inventory_history_architecture",
        "title": "Panchvaktra Temple, Mandi: ASI inventory account of history and architecture",
        "topic": "historical_background_architecture_religious_significance_heritage",
        "url": "https://ignca.gov.in/Asi_data/84884.pdf",
        "source_title": "Panchvaktra Temple (Mandi), monument inventory entry 118",
        "publisher": "Archaeological Survey of India record hosted by Indira Gandhi National Centre for the Arts",
        "source_type": "asi_monument_inventory_record",
        "publication_date": None,
        "page_ref": "PDF entry 118; notification reference F-4-1/52-A2 dated 28 July 1952; PDF text lines 2725–2735",
        "categories": ["historical_background", "architecture", "religious_cultural_significance", "heritage_conservation", "visitor_information"],
        "text": "The ASI monument-inventory entry identifies Panchvaktra as a Shiva temple in Mandi and describes it as a stone temple in the northern shikhara style. It notes a mandapa supported on four heavy pillars with pot-and-foliage ornament. The entry says an earlier temple at the site was destroyed by floods in the early eighteenth century and that Raja Sidhanath built the present temple at the same spot; it also assigns the temple to the fifteenth century. The source does not explain the chronology between these statements, so this profile preserves the source's ambiguity rather than reconciling it. It describes a subsidiary temple to the west as having the same design and date. The inventory lists government ownership, continuing religious use, ASI Chandigarh Circle administrative control and notification reference F-4-1/52-A2 dated 28 July 1952. Its approach fields name Shimla airport, Jogindernagar railway station and Mandi bus station, but these are inventory directions rather than a current transport advisory. Accessed 5 November 2026.",
    },
    {
        "temple_id": "asi_himachal_pra_14fdecc910252f5f",
        "document_id": "systematic_research_20261105_panchvaktra_location_district_administration",
        "title": "Panchvaktra Temple location in Mandi district",
        "topic": "basic_information_location",
        "url": "https://hpmandi.nic.in/places-of-interest/",
        "source_title": "Places of Interest",
        "publisher": "District Administration Mandi, Government of Himachal Pradesh",
        "source_type": "official_district_information_page",
        "publication_date": None,
        "page_ref": "HTML lines 115–117",
        "categories": ["basic_information_location"],
        "text": "The Mandi district administration's places-of-interest page locates Panchvaktra Mahadev Temple at the confluence of the Suketi and Beas rivers in Mandi town. The page lists the temple among the town's archaeological and religious sites. It does not provide current opening hours, entry fees, accessibility details, or specific visitor instructions. Accessed 5 November 2026.",
    },
    {
        "temple_id": "asi_himachal_pra_14fdecc910252f5f",
        "document_id": "systematic_research_20261105_panchvaktra_asi_flood_conservation_2012_13",
        "title": "Panchvaktra Temple: flood-protection work reported in 2012–13",
        "topic": "heritage_conservation",
        "url": "https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%20%202012%20-%202013%20%20A%20Review.pdf",
        "source_title": "Indian Archaeology 2012–13: A Review",
        "publisher": "Archaeological Survey of India / National Mission on Monuments and Antiquities",
        "source_type": "official_archaeological_conservation_report",
        "publication_date": None,
        "page_ref": "Printed page 317; section 330; PDF text lines 9022–9023",
        "categories": ["heritage_conservation"],
        "text": "The Archaeological Survey of India's 2012–13 review says work was in progress to reduce the risk of Beas River floodwaters entering Panchvaktra Temple. It reports that a retaining wall was provided on the river side and strengthened with concealed reinforced-concrete columns and tie-beams, with granular filling behind the wall toward the temple. This is a dated account of work in progress, not evidence that the work was completed or that it describes the present condition of the temple. Accessed 5 November 2026.",
    },
]


def main() -> None:
    docs_path = DATA / "raw" / "temple_sources.json"
    catalogue_path = DATA / "catalogue.json"
    plan_path = DATA / "research_plan_all_217.json"
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    temples = {t["id"]: t for t in catalogue}
    queue = {t["temple_id"]: t for t in plan["temples"]}
    added: list[str] = []
    for spec in ITEMS:
        temple = temples[spec["temple_id"]]
        text = " ".join(spec["text"].split())
        doc = {
            "document_id": spec["document_id"], "temple_id": spec["temple_id"],
            "temple_name": temple["canonical_name"], "state": temple.get("state"),
            "district": temple.get("district"), "topic": spec["topic"],
            "title": spec["title"], "source_title": spec["source_title"],
            "source_url": spec["url"], "publisher": spec["publisher"],
            "source_type": spec["source_type"], "language": "en",
            "publication_date": spec["publication_date"], "retrieval_date": CHECKED,
            "collection_timestamp": datetime.now(timezone.utc).isoformat(),
            "source_page_reference": spec["page_ref"],
            "content_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "verification_status": "source_review_pending",
            "review_status": "pending_human_review", "is_paraphrase": True,
            "text": text,
        }
        existing = next((d for d in docs if d.get("document_id") == doc["document_id"]), None)
        if existing is None:
            docs.append(doc)
            added.append(doc["document_id"])
        elif existing.get("content_hash") != doc["content_hash"]:
            raise ValueError(f"Refusing to overwrite changed checkpoint document {doc['document_id']}")
        if doc["document_id"] not in temple.setdefault("document_ids", []):
            temple["document_ids"].append(doc["document_id"])
        row = queue[spec["temple_id"]]
        for key in ("sources_inspected", "previously_inspected_source_urls"):
            if spec["url"] not in row.setdefault(key, []):
                row[key].append(spec["url"])
        row["research_status"] = "enriched"
        row["enrichment_status"] = "enriched"
        row["last_completed_checkpoint"] = "2026-11-05-group17"
        row["documents_added_this_operation"] = sorted(set(row.get("documents_added_this_operation", [])) | {doc["document_id"]})
        row["page_evidence_categories"] = sorted(set(row.get("page_evidence_categories", [])) | set(spec["categories"]))
        note = f"Inspected {spec['source_title']} ({spec['url']}); relevant section {spec['page_ref']}. New document remains pending human review."
        if note not in row.setdefault("research_notes", []):
            row["research_notes"].append(note)
    checks = plan.setdefault("source_checks_this_operation", [])
    checks_by_url = {c.get("source_url"): c for c in checks}
    for url in sorted({i["url"] for i in ITEMS}):
        entries = [i for i in ITEMS if i["url"] == url]
        first = entries[0]
        record = {
            "source_title": first["source_title"], "source_url": url,
            "publisher": first["publisher"], "source_type": first["source_type"],
            "publication_date": first["publication_date"], "accessed_date": CHECKED,
            "linked_temple_ids": sorted({i["temple_id"] for i in entries}),
            "categories_with_relevant_source_content": sorted({c for i in entries for c in i["categories"]}),
            "inspection_method": "Opened the actual report/PDF and inspected the cited section; source page references are recorded in the knowledge documents.",
            "note": "Claims remain pending human review. The Panchvaktra source's chronology ambiguity is preserved.",
        }
        if url in checks_by_url:
            checks_by_url[url].update(record)
        else:
            checks.append(record)
    nmaa_url = "https://nmma.nic.in/nmma/builtDetail.do?dynasty=59&refId=2740"
    failures = plan.setdefault("inaccessible_or_unmapped_source_attempts", [])
    failed = next((x for x in failures if x.get("source_url") == nmaa_url), None)
    failure = {
        "source_url": nmaa_url,
        "linked_temple_ids": ["asi_himachal_pra_f2a74ffbd1613f95"],
        "attempted_date": CHECKED,
        "status": "page_fetch_timeout",
        "note": "Direct page open timed out. Search indexing text was not treated as inspected source evidence; no claims from this page were used.",
    }
    if failed:
        failed.update(failure)
    else:
        failures.append(failure)
    plan["last_checkpoint"] = "2026-11-05-group17"
    plan["last_updated_utc"] = datetime.now(timezone.utc).isoformat()
    for path, value in ((docs_path, docs), (catalogue_path, catalogue), (plan_path, plan)):
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"catalogue": len(catalogue), "documents": len(docs), "documents_added": added, "source_urls_used": len({i['url'] for i in ITEMS})}, indent=2))


if __name__ == "__main__":
    main()
