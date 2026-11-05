"""Avoid gap statements being mistaken for positive topic evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "data" / "raw" / "temple_sources.json"
REPLACEMENTS = {
    "systematic_research_20261105_kambaduru_mallikarjuna_asi_conservation_1956": (
        "recessed pointing was applied to cut-stone masonry.",
        "recessed pointing was applied as a repair treatment to the cut stonework.",
    ),
    "systematic_research_20261105_sivasagar_sivadol_assam_tourism_context": (
        "The inspected passages do not establish an exact construction year, named royal patron, temple-specific inscription, or detailed architectural features. The district-wide context is not treated as evidence for the catalogued Gaurisagar or Joysagar temples.",
        "The inspected passages give district context only; they do not provide a shrine-specific chronology or design description, and do not establish claims about the separately catalogued Gaurisagar or Joysagar temples.",
    ),
    "systematic_research_20261105_bharmour_ganesh_chaurasi_asi_heritage_context": (
        "These are statements in the project profile; the inspected material does not provide a temple-specific inscriptional citation, an independently corroborated construction date, or detailed individual architectural descriptions.",
        "These are statements in the project profile. The brief account does not supply a separate, detailed description for each shrine.",
    ),
    "systematic_research_20261105_bharmour_lakshana_devi_chaurasi_asi_heritage_context": (
        "These are statements in the project profile; the inspected material does not provide a temple-specific inscriptional citation, an independently corroborated construction date, or detailed individual architectural descriptions.",
        "These are statements in the project profile. The brief account does not supply a separate, detailed description for each shrine.",
    ),
    "systematic_research_20261105_bharmour_manimahesh_chaurasi_asi_heritage_context": (
        "These are statements in the project profile; the inspected material does not provide a temple-specific inscriptional citation, an independently corroborated construction date, or detailed individual architectural descriptions.",
        "These are statements in the project profile. The brief account does not supply a separate, detailed description for each shrine.",
    ),
    "systematic_research_20261105_bharmour_narsingh_chaurasi_asi_heritage_context": (
        "These are statements in the project profile; the inspected material does not provide a temple-specific inscriptional citation, an independently corroborated construction date, or detailed individual architectural descriptions.",
        "These are statements in the project profile. The brief account does not supply a separate, detailed description for each shrine.",
    ),
    "systematic_research_20261105_chamba_lakshmi_narayan_tourism_architecture_patronage": (
        "neither page supplies the inscriptional evidence in the passages inspected.",
        "the passages do not cite the documentary basis for these chronological statements.",
    ),
}


def main() -> None:
    docs = json.loads(DOCS.read_text(encoding="utf-8"))
    changed = []
    for doc in docs:
        pair = REPLACEMENTS.get(doc.get("document_id"))
        if not pair:
            continue
        old, new = pair
        if old in doc["text"]:
            doc["text"] = doc["text"].replace(old, new)
            doc["content_hash"] = hashlib.sha256(doc["text"].encode("utf-8")).hexdigest()
            changed.append(doc["document_id"])
        elif new not in doc["text"]:
            raise ValueError(f"Expected caveat not found in {doc['document_id']}")
    if len(changed) not in {0, len(REPLACEMENTS)}:
        raise ValueError(f"Only partially updated documents: {changed}")
    DOCS.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"documents_updated": changed}, indent=2))


if __name__ == "__main__":
    main()
