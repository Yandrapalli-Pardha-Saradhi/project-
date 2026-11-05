"""Record temple-specific material read in the NCF/ASI Shimla Circle PDF."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TODAY = "2026-11-05"
URL = "https://ncf.nic.in/assets/images/Himachal%20under%20Shimal%20Circle.pdf"
SOURCE_TITLE = "Monuments of Himachal Pradesh under Shimla Circle"
PUBLISHER = "National Culture Fund-hosted Shimla Circle heritage profile"
SOURCE_TYPE = "ncf_hosted_heritage_profile_pdf"


def main() -> None:
    cat_path = DATA / "catalogue.json"
    docs_path = DATA / "raw" / "temple_sources.json"
    plan_path = DATA / "research_plan_all_217.json"
    catalogue = json.loads(cat_path.read_text(encoding="utf-8"))
    docs = json.loads(docs_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    by_id = {t["id"]: t for t in catalogue}
    ids = {
        "hidimba": "asi_himachal_pra_aac4a2248ad925db",
        "chamunda_chamba": "asi_himachal_pra_2cd9e34ca0dd4e17",
        "shakti_chhatari": "asi_himachal_pra_29892a543f8e7863",
        "basheshar_bajaura": "asi_himachal_pra_2d93808a25e7f773",
        "gauri_dassal": "asi_himachal_pra_9681bf3ab0a6c3f8",
        "gauri_naggar": "asi_himachal_pra_53211815add81171",
        "lakshmi_narayan": "asi_himachal_pra_a6a66c91268cdcdf",
    }
    seen = {d.get("document_id") for d in docs}

    def add(key: str, slug: str, title: str, topic: str, content: str) -> None:
        tid = ids[key]
        did = f"systematic_research_20261105_{slug}"
        if did in seen:
            return
        temple = by_id[tid]
        text = content + " Accessed 2026-11-05. PDF section: named temple profile; the PDF extractor did not expose a reliable printed page number."
        docs.append({
            "document_id": did, "temple_id": tid,
            "temple_name": temple.get("canonical_name") or temple.get("names", [tid])[0],
            "state": temple.get("state"), "district": temple.get("district"),
            "topic": topic, "title": title, "source_title": SOURCE_TITLE,
            "source_url": URL, "publisher": PUBLISHER, "source_type": SOURCE_TYPE,
            "language": "en", "publication_date": None, "retrieval_date": TODAY,
            "collection_timestamp": datetime.now(timezone.utc).isoformat(),
            "content_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "verification_status": "source_review_pending", "review_status": "pending_human_review",
            "is_paraphrase": True, "text": text,
        })
        seen.add(did)
        refs = temple.setdefault("document_ids", [])
        if did not in refs:
            refs.append(did)

    add("hidimba", "manali_hidimba_ncf_inscription_architecture_protection",
        "Hidimba Devi Temple: inscription, wooden construction and ASI status in Shimla Circle profile",
        "history_architecture_heritage_conservation",
        "The Shimla Circle profile reproduces the temple information sign, which says an inscription on a wooden panel beside the entrance records that Raja Bahadur Singh caused the temple to be built in a year corresponding to 1553 CE. The sign describes a three-tier wooden-plank roof and a metal umbrella and finial as a fourth roof, a raised verandah, carved façades and windows, a wooden balcony, and a carved four-part doorframe. It lists images on the doorway including Mahishasuramardini, Shiva with Parvati on Nandi, Durga, Vishnu with Lakshmi on Garuda, Ganesha and Navagraha panels. The sign reports protection as a monument of national importance under notification P.4/4/67 dated 18 April 1967. The same profile separately describes a rock in the sanctum as a meditation place associated with Hidimba; this is reported tradition, not a historical inscription claim.")
    add("chamunda_chamba", "chamba_chamunda_ncf_architecture_history_conflict",
        "Chamunda Devi Temple, Chamba: Shimla Circle profile and unresolved chronology",
        "history_architecture_religious_cultural_significance_heritage_conservation",
        "The Shimla Circle profile explicitly identifies Shri Chamunda Devi Temple in Chamba district. It describes a pent-roof vernacular Himachali wooden temple, with carved wooden façade and shikhara-like tower, and attributes royal patronage to Chambial rulers. It reports a local account of the goddess Chamunda defeating Chanda and Munda and says the temple is believed to date to around the 18th century under Raja Umed Singh. The same profile also says the temple suffered extensive damage during an attack by the Nurpur rulers in 1641 CE. These statements create an unresolved chronology conflict within the profile; they are preserved as attributed source claims and are not presented as reconciled historical facts.")
    add("shakti_chhatari", "chhatari_shakti_devi_ncf_wooden_architecture_history",
        "Shakti Devi Temple, Chhatari: Shimla Circle profile on wooden architecture and attribution",
        "history_architecture_religious_cultural_significance",
        "The Shimla Circle profile describes the Chhatari Shakti Devi temple as a classical wooden temple of the Himalayan region, with similarities to the Lakshana Devi shrine. It dates the temple broadly to about 700 CE and attributes its construction to King Meruverman; the profile says an inscription on a pedestal at the Lakshana Devi temple records construction by Gugga under King Meru Verman's order. That inscription is at the Lakshana shrine, not at the Shakti Devi temple, so the builder statement is retained as the profile's attribution rather than direct inscriptional evidence at Chhatari. The document describes the temple facing west and an Ashtadhatu image of Shakti Devi in the sanctum.")
    add("basheshar_bajaura", "bajaura_basheshar_ncf_architecture_date_comparison",
        "Basheshar Mahadev, Bajaura: Shimla Circle profile on layout and dating",
        "history_architecture_religious_cultural_significance",
        "The Shimla Circle profile identifies Basheshar Mahadev at Bajaura in Kullu district, also called Vishveshvara Mahadev, and describes it as a Shiva temple with a lingam in the sanctum. The profile calls its style Nagara and dates it to the 8th or 9th century CE; it describes a square plan with four graduated projections and an east-facing doorway. Himachal Tourism's separately inspected page gives a broader 9th-to-12th-century date for the Bajaura Basheshara/Vishveshvara temple. These date ranges overlap only at the 9th century and remain distinct source attributions pending review.")
    add("gauri_dassal", "dassal_gauri_shankar_ncf_architecture_sculpture",
        "Gauri Shankar Temple, Dassal: Shimla Circle architectural description",
        "history_architecture_religious_cultural_significance",
        "The Shimla Circle profile places the Gauri Shankar temple in Dassal village, about 24 km from Kullu and 6 km from Patlikuhal, and dates it to the 9th–10th centuries CE in shikhara style. It describes a garbhagriha and mandapa, with a Shiva lingam as the presiding object of worship, and two pillars at the entrance mandapa. The profile describes figures of Shiva, Ganga, Yamuna and dvarapalas, two rows of exterior niches, and a Nandi placed outside. The profile's travel distances are historical/source-specific and are not presented as current route guidance.")
    add("gauri_naggar", "naggar_gauri_shankar_ncf_architecture_sculpture",
        "Gauri Shankar Temple, Naggar: Shimla Circle architectural description",
        "history_architecture_religious_cultural_significance",
        "The Shimla Circle profile separately identifies the Gauri Shankar temple at Naggar and dates it to the 9th–10th centuries CE. It describes a stone Nagara-type structure dedicated to Shiva and known for stone carvings. The profile notes that some castle-like and ornamental details may have been restored later. These remarks concern the Naggar temple and are not transferred to the distinct Gauri Shankar temple at Dassal.")
    add("lakshmi_narayan", "chamba_lakshmi_narayan_ncf_icon_patronage",
        "Lakshmi Narayan Temple, Chamba: Shimla Circle profile on deity and patronage",
        "history_religious_cultural_significance_architecture",
        "The Shimla Circle profile calls Lakshmi Narayan the best-known temple of Chamba and identifies a large white-marble image of Lakshmi Narayan, said by the source to be from the Vindhya region, as the principal image. It attributes patronage to Sahil Varman and gives a 920–940 CE range. It describes a six-temple complex arranged north to south and reports shrines dedicated to Shiva and Vishnu. This supports a 10th-century patronage account, while the separate Government of Himachal Pradesh pilgrimage page's broad 8th-century date for the group remains a conflicting source claim requiring review.")

    plan.setdefault("source_checks_this_operation", []).append({
        "source_title": SOURCE_TITLE, "source_url": URL, "publisher": PUBLISHER,
        "source_type": SOURCE_TYPE, "publication_date": None, "accessed_date": TODAY,
        "linked_temple_ids": list(ids.values()),
        "categories_with_relevant_source_content": ["historical_background", "architecture", "religious_cultural_significance", "inscriptions_historical_evidence", "heritage_conservation"],
        "inspection_method": "Opened the NCF-hosted PDF and inspected its titled Shimla Circle temple profiles for the exact named entries. Temple-locality matches were cross-checked against the catalogue; no bulk download or crawl was performed.",
        "note": "The profile mixes reproduced site-sign text, project descriptions and proposed visitor works; no publication date was apparent in the inspected pages. Date conflicts and attributed inscription claims are explicitly retained. Only temple-specific sections are used.",
    })
    unique = {}
    for check in plan["source_checks_this_operation"]:
        unique[(check.get("source_url"), tuple(sorted(check.get("linked_temple_ids", []))))] = check
    plan["source_checks_this_operation"] = list(unique.values())
    added = [
        "systematic_research_20261105_manali_hidimba_ncf_inscription_architecture_protection",
        "systematic_research_20261105_chamba_chamunda_ncf_architecture_history_conflict",
        "systematic_research_20261105_chhatari_shakti_devi_ncf_wooden_architecture_history",
        "systematic_research_20261105_bajaura_basheshar_ncf_architecture_date_comparison",
        "systematic_research_20261105_dassal_gauri_shankar_ncf_architecture_sculpture",
        "systematic_research_20261105_naggar_gauri_shankar_ncf_architecture_sculpture",
        "systematic_research_20261105_chamba_lakshmi_narayan_ncf_icon_patronage",
    ]
    plan["last_checkpoint"] = {
        "checkpoint_id": "systematic_research_20261105_himachal_group_08",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "temple_ids": list(ids.values()), "documents_added": [x for x in added if x in seen],
        "note": "Inspected NCF/ASI Shimla Circle PDF temple profiles; all new documents are pending human review and conflicts remain attributed.",
    }
    cat_path.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    docs_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"catalogue": len(catalogue), "documents": len(docs), "added": plan["last_checkpoint"]["documents_added"]}, indent=2))


if __name__ == "__main__":
    main()
