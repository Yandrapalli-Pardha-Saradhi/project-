"""Record temple-specific evidence inspected in UNESCO's Hoysala nomination dossier."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
URL = "https://whc.unesco.org/document/198086"
SOURCE_TITLE = "World Heritage Site Nomination Dossier: Sacred Ensembles of the Hoysalas (Supplementary Information)"
PUBLISHER = "Government of India / Government of Karnataka, submitted to UNESCO World Heritage Centre"
CHECKED = "2026-11-05"
ITEMS = [
    {
        "temple_id": "asi_karnataka_2afd54b8e1b183a7",
        "document_id": "systematic_research_20261105_hariharesvara_harihar_hoysala_dossier_history_architecture",
        "title": "Harihareshvara Temple, Harihar: Hoysala-period history, inscriptions and architecture",
        "topic": "history_architecture_religious_significance",
        "pages": "printed pages 16–17; PDF lines 3124–3168",
        "categories": ["historical_background", "architecture", "religious_cultural_significance", "inscriptions_historical_evidence", "heritage_conservation"],
        "text": "The supplementary inventory in the Sacred Ensembles of the Hoysalas nomination dossier identifies the Harihareshvara Temple at Harihar, in the dossier's spelling Devanagere, as a living temple dedicated to Harihara, the combined form of Shiva and Vishnu. The dossier dates the building to 1224 CE and attributes its commissioning to Polalva, a general of Hoysala king Narasimha II. It reports that inscriptions record endowments by the Pandya rulers of Uchchangi and Vijayanagara rulers; it does not reproduce those inscriptions here. The building is described as chloritic-schist stone, granite and brick masonry, with an indented sanctum, antarala, navaranga and mahamandapa arranged east–west. The northern and southern entrances lead to porches; the north porch was extended and adapted as an antarala for a subsidiary shrine. The dossier describes a 1.21-metre Harihara image whose two halves carry Vishnu's chakra and conch and Shiva's trident and rosary. A Lakshmi shrine adjoins the main sanctum, and another Hariharesvara shrine is built into the west enclosure wall. It counts 56 circular lathe-turned pillars supporting an S-shaped eave and characterizes the plan as an ekakuta with a semi-stellate pattern. The dossier says the monument is protected and maintained by ASI and that worship/festivals are managed by Karnataka's MUZRAI department, but supplies no festival names or calendar. This temple appears in supplementary inventory material; that inclusion alone does not make it one of the three components inscribed as the Sacred Ensembles of the Hoysalas. Source section inspected, printed pages 16–17 (PDF lines 3124–3168); accessed 5 November 2026."
    },
    {
        "temple_id": "asi_karnataka_e1c13713806e44d6",
        "document_id": "systematic_research_20261105_isvara_arsikere_hoysala_dossier_history_architecture",
        "title": "Isvara Temple, Arsikere: Hoysala patronage, shrines and stellate design",
        "topic": "history_architecture_religious_significance",
        "pages": "printed pages 18–20; PDF lines 3171–3222",
        "categories": ["historical_background", "architecture", "religious_cultural_significance", "heritage_conservation"],
        "text": "The Sacred Ensembles of the Hoysalas supplementary inventory describes Isvara Temple at Arsikere as a living Shiva temple built in chloritic schist and attributes it to Hoysala king Vira Ballala II, giving 1220 CE as its establishment date. Its account distinguishes an ekakuta shrine with an open mukha-mandapa from a dvikuta shrine with a shared pillared mandapa, all within a compound wall. It names the Shiva forms in the shrines as Chandramoulesvara, Veereshvara and Bakkeshvara. The main shrine sequence includes a porch, closed navaranga, open antarala and sanctum. The dossier emphasizes an unusual combination of stellate plans: a sixteen-pointed star plan in both sanctum and mukha-mandapa, with differing profiles, and a five-tier Vesara superstructure following the sanctum's plan. It also describes varied ceiling types and a highly ornamented six-tier domed ceiling in the mukha-mandapa, as well as sculpted exterior walls. These descriptions are the dossier authors' architectural interpretation and are not a separate UNESCO inscription or recognition of this individual temple. The inspected section supplies no festival calendar, current visitor timings, or entry information. Source section inspected, printed pages 18–20 (PDF lines 3171–3222); accessed 5 November 2026."
    },
    {
        "temple_id": "asi_karnataka_03633ec3263fe299",
        "document_id": "systematic_research_20261105_lakshmidevi_doddagaddavalli_hoysala_dossier_history_architecture",
        "title": "Lakshmidevi Temple, Doddagadavalli: foundation, four-spired plan and iconography",
        "topic": "history_architecture_religious_significance",
        "pages": "printed pages 33–35; PDF lines 3519–3568",
        "categories": ["historical_background", "architecture", "religious_cultural_significance", "inscriptions_historical_evidence", "heritage_conservation"],
        "text": "The supplementary inventory for the Sacred Ensembles of the Hoysalas identifies Lakshmidevi Temple at Doddagadavalli (the catalogue locality is spelled Doddgaddavalli) as a living temple made of chloritic schist. It says merchant Kullahana Rahuta and his wife Sajajadevi commissioned it in 1113 CE and calls it one of the oldest recognizably Hoysala temples. The dossier records historic names for the settlement—Gadduballi, Dakshina Kollapurava and Abhinava Kollapura—while its comparison with the Kolhapur Mahalakshmi site is contextual rather than proof of a direct institutional relationship. The compound is described as centered on a four-spired chatushkuta shrine aligned to cardinal directions, with four smaller corner shrines on the compound wall aligned to ordinal directions. The dossier also notes an eastern pillared entrance with dvarapalas and a western Bhairava shrine it considers a later addition. Two ceiling panels depict the ashtadikpalakas. The dossier distinguishes sculptural modes and discusses images including Mahalakshmi, Mahakali and a possibly identified Bhutanatha linga; it reports that only three of nine original cult images remain intact and says the Virabhadra now in the south-facing Vishnu shrine is a recent replacement, without dating that replacement. Its phrase “Kadamba Nagara” is presented as a label sometimes used, while the dossier discusses Early Chalukyan resonances and competing stylistic interpretations. The temple's appearance in a supplementary nomination inventory does not mean that this individual temple is itself a component of the property inscribed in 2023. The inspected section provides no current festival schedule, opening hours, or fees. Source section inspected, printed pages 33–35 (PDF lines 3519–3568); accessed 5 November 2026."
    },
    {
        "temple_id": "asi_karnataka_4e9044ce27267cfb",
        "document_id": "systematic_research_20261105_viranarayana_belavadi_hoysala_dossier_architecture_history",
        "title": "Viranarayana Temple, Belavadi: three-shrine Hoysala plan and sculptural program",
        "topic": "historical_architecture_religious_significance_heritage",
        "pages": "printed pages 29–32; PDF lines 3446–3493",
        "categories": ["historical_background", "architecture", "religious_cultural_significance", "heritage_conservation"],
        "text": "The supplementary inventory in the Sacred Ensembles of the Hoysalas nomination dossier describes Viranarayana Temple at Belavadi as a living Vaishnava temple in chloritic schist. It gives 1206 CE and reports the attribution to Hoysala king Veera Ballala or Narasimha Ballala as coming from the head priest; this is retained as an attributed account rather than independent inscriptional proof. The dossier describes the present temple as a trikuta (three-celled) complex that developed from an earlier ekakuta plan. It identifies the western main shrine with Veera Narayana, the southern subsidiary shrine with Venu Gopala and the northern one with Yoga Narasimha. The dossier suggests, rather than proves, that the additions occurred in phases, and says the side-shrine arrangement may reflect the popularity of Venu Gopala and Narasimha forms. The shrine complex has an eastern main entrance, an antarala, a closed navaranga and a semi-open mandapa. The Yoga Narasimha shrine has a semi-stellate plan, while the two other shrine plans are linear; the three Vesara superstructures follow those distinct profiles. The inventory contrasts the plain exterior of the central western shrine with figure sculpture on the side shrines, and notes varied pillar forms, polished lathe-turned pillars and elephant figures supporting the kakshasana seats. It also mentions serial Bhagavata scenes among dancers and musicians on the exterior seating backrest. The report calls the site ASI centrally protected and states that from 1760 the temple was under Sringeri Matha, which paid daily worship expenses; these are statements in the dossier, not current visitor information. The dossier's appearance as supplementary inventory should not be confused with individual inscription on the World Heritage List: the inscribed serial property's components are three other named temples. No specific festival names or current visiting hours are supplied in this section. Source section inspected, printed pages 29–32 (PDF lines 3446–3493); accessed 5 November 2026."
    },
]


def main() -> None:
    docs_path = DATA / "raw" / "temple_sources.json"
    catalogue_path = DATA / "catalogue.json"
    plan_path = DATA / "research_plan_all_217.json"
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in catalogue}
    queue = {r["temple_id"]: r for r in plan["temples"]}
    added = []
    for spec in ITEMS:
        temple = by_id[spec["temple_id"]]
        text = " ".join(
            spec["text"]
            .replace("No specific festival names or current visiting hours are supplied in this section.", "")
            .replace("these are statements in the dossier, not current visitor information", "these are reported in the dossier and are not current administrative details")
            .split()
        )
        doc = {
            "document_id": spec["document_id"], "temple_id": spec["temple_id"],
            "temple_name": temple["canonical_name"], "state": temple["state"],
            "district": temple["district"], "topic": spec["topic"], "title": spec["title"],
            "source_title": SOURCE_TITLE, "source_url": URL, "publisher": PUBLISHER,
            "source_type": "official_world_heritage_nomination_supplementary_inventory",
            "language": "en", "publication_date": None, "retrieval_date": CHECKED,
            "collection_timestamp": datetime.now(timezone.utc).isoformat(),
            "source_page_reference": spec["pages"],
            "content_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "verification_status": "source_review_pending", "review_status": "pending_human_review",
            "is_paraphrase": True, "text": text,
        }
        old = next((d for d in docs if d.get("document_id") == spec["document_id"]), None)
        if old is None:
            docs.append(doc)
            added.append(spec["document_id"])
        elif old.get("content_hash") != doc["content_hash"]:
            old.update(doc)
        if spec["document_id"] not in temple.setdefault("document_ids", []):
            temple["document_ids"].append(spec["document_id"])
        row = queue[spec["temple_id"]]
        for field in ("sources_inspected", "previously_inspected_source_urls"):
            if URL not in row.setdefault(field, []):
                row[field].append(URL)
        row["research_status"] = "enriched"
        row["enrichment_status"] = "enriched"
        row["last_completed_checkpoint"] = "2026-11-05-group15"
        row["documents_added_this_operation"] = sorted(set(row.get("documents_added_this_operation", [])) | {spec["document_id"]})
        row["page_evidence_categories"] = sorted(set(row.get("page_evidence_categories", [])) | set(spec["categories"]))
        row.setdefault("research_notes", []).append(f"Inspected exact temple inventory section in UNESCO-hosted supplementary nomination dossier, {spec['pages']}; inclusion is not treated as individual UNESCO inscription.")
    # Correct the earlier source label for this same PDF after inspecting its
    # cover and named Belavadi section. Preserve its text and review state.
    prior_belavadi = next((d for d in docs if d.get("document_id") == "enrich_20261105_asi_karnataka_4e9044ce27267cfb"), None)
    if prior_belavadi and prior_belavadi.get("source_url") == URL:
        prior_belavadi.update({
            "source_title": SOURCE_TITLE,
            "publisher": PUBLISHER,
            "source_type": "official_world_heritage_nomination_supplementary_inventory",
        })
    check = {
        "source_title": SOURCE_TITLE, "source_url": URL, "publisher": PUBLISHER,
        "source_type": "official_world_heritage_nomination_supplementary_inventory",
        "publication_date": None, "accessed_date": CHECKED,
        "linked_temple_ids": [i["temple_id"] for i in ITEMS],
        "categories_with_relevant_source_content": sorted({c for i in ITEMS for c in i["categories"]}),
        "inspection_method": "Opened the actual UNESCO-hosted PDF and read each named temple's inventory section; relevant printed pages and extracted PDF line ranges are recorded in each document.",
        "note": "This is supplementary material in the Sacred Ensembles of the Hoysalas nomination dossier; individual entries are not represented as UNESCO-inscribed components. No automated collection was run.",
    }
    checks = plan.setdefault("source_checks_this_operation", [])
    existing_check = next((c for c in checks if c.get("source_url") == URL), None)
    if existing_check:
        existing_check.update(check)
    else:
        checks.append(check)
    for path, value in ((docs_path, docs), (catalogue_path, catalogue), (plan_path, plan)):
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"catalogue": len(catalogue), "documents": len(docs), "added": added, "source_url": URL}, indent=2))


if __name__ == "__main__":
    main()
