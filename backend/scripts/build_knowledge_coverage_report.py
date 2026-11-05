"""Create a deterministic, heuristic coverage audit for the temple catalogue."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

DATA = Path(__file__).resolve().parents[1] / "data"
CATALOGUE = DATA / "catalogue.json"
DOCUMENTS = DATA / "raw" / "temple_sources.json"
OUTPUT = DATA / "knowledge_coverage_report.json"

TOPIC_PATTERNS = {
    "historical_background_timeline": re.compile(r"\b(history|historical|centur(?:y|ies)|dated|built|construction|timeline|antiquity|medieval|early)\b", re.I),
    "kings_dynasties_contributors": re.compile(r"\b(dynast(?:y|ic|ies)|king|queen|ruler|emperor|patron|reign|chola|pallava|hoysala|kakatiya|ganga|chalukya|somavamsi|vijayanagara)\b", re.I),
    "architecture_construction": re.compile(r"\b(architect(?:ure|ural)|vimana|mandapa|gopuram|gopura|sanctum|shrine|pillars?|tower|plan|stonework|kalinga|dravidian|nagara|foundation|layout|stone chariot|structural)\b", re.I),
    "sculpture_inscriptions_distinctive_structures": re.compile(r"\b(sculpt(?:ure|ed|ures)|inscription|epigraph|carving|relief|frieze|mural|panel|monolith|lattice|bas[- ]relief)\b", re.I),
    "deity_religious_cultural_significance": re.compile(r"\b(deit(?:y|ies)|shiva|vishnu|krishna|devi|goddess|surya|worship|religious|cultural|sacred|pilgrimage|tradition|devotional)\b", re.I),
    "festivals_rituals_traditions": re.compile(r"\b(festival|ritual|procession|rath yatra|shivaratri|brahmotsavam|celebration|observance|ceremony|prasad|wedding)\b", re.I),
    "heritage_conservation_visitor_information": re.compile(r"\b(unesco|world heritage|conservation|protected|restoration|preservation|archaeological survey|asi |visitor|visiting hours|entry|ticket|maintenance)\b", re.I),
}
INVENTORY_MARKERS = ("asi_inventory", "inventory listing", "protected monuments list")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    catalogue = load(CATALOGUE)
    documents = load(DOCUMENTS)
    if not isinstance(catalogue, list) or not isinstance(documents, list):
        raise SystemExit("Catalogue and knowledge documents must be JSON arrays")
    docs_by_temple: dict[str, list[dict]] = defaultdict(list)
    for doc in documents:
        if isinstance(doc, dict) and isinstance(doc.get("temple_id"), str):
            docs_by_temple[doc["temple_id"]].append(doc)

    batches = []
    previously_enriched: set[str] = set()
    for path in sorted(DATA.glob("enrichment_manifest_batch_*.json")):
        manifest = load(path)
        ids = [row.get("temple_id") for row in manifest.get("temples", []) if isinstance(row, dict)]
        batches.append({
            "manifest": path.name,
            "batch_id": manifest.get("batch_id"),
            "manifest_temple_count": len(ids),
            "counts": manifest.get("counts", {}),
            "scope_temple_ids": ids,
        })
        previously_enriched.update(ids)

    rows = []
    priorities = []
    coverage_counts: Counter[str] = Counter()
    review_counts: Counter[str] = Counter()
    topic_coverage_counts: Counter[str] = Counter()
    for temple in catalogue:
        temple_id = temple.get("id")
        linked = docs_by_temple.get(temple_id, [])
        category_evidence: dict[str, list[str]] = defaultdict(list)
        useful_docs = 0
        inventory_docs = 0
        pending_docs = 0
        unknown_review_docs = 0
        source_domains = set()
        topical_source_domains = set()
        source_urls = set()
        for doc in linked:
            text = str(doc.get("text") or "")
            topic = str(doc.get("topic") or "")
            source_type = str(doc.get("source_type") or "")
            marker = f"{topic} {source_type} {doc.get('source_title', '')}".casefold()
            inventory = any(term in marker for term in INVENTORY_MARKERS)
            if inventory:
                inventory_docs += 1
            else:
                useful_docs += 1
            review = str(doc.get("review_status") or doc.get("verification_status") or "unlabelled")
            if "pending" in review.casefold() or "needs_review" in review.casefold():
                pending_docs += 1
            elif review == "unlabelled":
                unknown_review_docs += 1
            host = ""
            if doc.get("source_url"):
                source_urls.add(doc["source_url"])
                host = (urlsplit(doc["source_url"]).hostname or "").casefold()
                if host:
                    source_domains.add(host.removeprefix("www."))
            evidence_text = f"{topic} {doc.get('source_title', '')} {text}"
            if not inventory:
                if host:
                    topical_source_domains.add(host.removeprefix("www."))
                for category, pattern in TOPIC_PATTERNS.items():
                    if pattern.search(evidence_text):
                        category_evidence[category].append(doc.get("document_id", "(missing id)"))

        covered = sorted(category_evidence)
        topic_count = len(covered)
        if useful_docs == 0:
            coverage = "basic"
        elif useful_docs >= 5 and topic_count >= 5 and len({d.get("source_url") for d in linked if d.get("source_url") and not any(term in f"{d.get('topic', '')} {d.get('source_type', '')} {d.get('source_title', '')}".casefold() for term in INVENTORY_MARKERS)}) >= 3:
            coverage = "comprehensive"
        elif useful_docs >= 3 and topic_count >= 3:
            coverage = "moderate"
        else:
            coverage = "limited"
        coverage_counts[coverage] += 1
        if pending_docs:
            review_counts["has_pending_review_document"] += 1
        if unknown_review_docs:
            review_counts["has_unlabelled_document"] += 1
        for topic in covered:
            topic_coverage_counts[topic] += 1
        missing = [topic for topic in TOPIC_PATTERNS if topic not in category_evidence]
        authority_rank = max((5 if "whc.unesco.org" in host else 4 if any(x in host for x in ("asi.nic.in", "nma.gov.in", "nmma.nic.in", "tnarch.gov.in")) else 3 if host.endswith(".gov.in") or host.endswith(".nic.in") else 2 for host in topical_source_domains), default=0)
        # Inventory-only sources are authoritative location records but are not
        # treated as evidence for the unfilled historical/cultural topics.
        gap_score = len(missing)
        priority_score = round(gap_score * (1 + authority_rank / 5), 2)
        row = {
            "temple_id": temple_id,
            "name": temple.get("canonical_name") or (temple.get("names") or [temple_id])[0],
            "alternate_names": temple.get("alternate_names") or temple.get("names", []),
            "state": temple.get("state"),
            "district": temple.get("district"),
            "area": temple.get("area"),
            "document_count": len(linked),
            "useful_non_inventory_document_count": useful_docs,
            "inventory_document_count": inventory_docs,
            "coverage_class": coverage,
            "topic_count_heuristic": topic_count,
            "topics_with_document_evidence": covered,
            "document_ids_by_topic": {k: sorted(set(v)) for k, v in category_evidence.items()},
            "missing_topics": missing,
            "source_domains": sorted(source_domains),
            "topical_source_domains": sorted(topical_source_domains),
            "source_urls": sorted(source_urls),
            "pending_review_document_count": pending_docs,
            "unlabelled_review_document_count": unknown_review_docs,
            "prior_enrichment_manifest_scope": temple_id in previously_enriched,
            "priority_score": priority_score,
        }
        rows.append(row)
        if coverage != "comprehensive":
            priorities.append(row)

    priorities.sort(key=lambda r: (-r["priority_score"], -r["document_count"], r["state"] or "", r["name"].casefold()))
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "snapshot_scope": "Current catalogue and linked knowledge documents at report generation time.",
        "catalogue_record_count": len(catalogue),
        "knowledge_document_count": len(documents),
        "method": {
            "classification": "Heuristic audit of linked document topic/source metadata and text keyword evidence; it is a triage report, not claim verification.",
            "basic": "Only inventory/location records and no useful topical document.",
            "limited": "One or two useful topical documents, or at most two topical evidence categories detected.",
            "moderate": "Several topical categories detected, but the document count or topic spread is below the comprehensive threshold.",
            "comprehensive": "At least five non-inventory documents, five topical categories, and three distinct topical source URLs; human review is still required for source support and depth.",
            "pending_review_is_not_verified": True,
        },
        "summary": {
            "coverage_class_counts": {
                name: coverage_counts.get(name, 0)
                for name in ("basic", "limited", "moderate", "comprehensive")
            },
            "topic_temple_counts": dict(topic_coverage_counts),
            "temples_with_pending_review_documents": review_counts["has_pending_review_document"],
            "temples_with_unlabelled_document_status": review_counts["has_unlabelled_document"],
            "temples_with_prior_enrichment_manifest_entries": len(previously_enriched),
            "prior_enrichment_manifests": batches,
        },
        "prioritized_100": priorities[:100],
        "temples": rows,
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(OUTPUT), "temples": len(rows), "documents": len(documents), "coverage": dict(coverage_counts), "priority_list": min(100, len(priorities))}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
