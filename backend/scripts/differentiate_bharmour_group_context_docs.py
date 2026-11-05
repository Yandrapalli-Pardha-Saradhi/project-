"""Make shared Chaurasi source context entity-explicit in each document."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
DOCS = DATA / "raw" / "temple_sources.json"
TARGETS = {
    "systematic_research_20261105_bharmour_ganesh_chaurasi_asi_heritage_context":
        "The inspected 2019 profile explicitly names the Ganesh Temple at Bharmour as one of the four Chaurasi shrines under ASI Shimla Circle jurisdiction. ",
    "systematic_research_20261105_bharmour_lakshana_devi_chaurasi_asi_heritage_context":
        "The inspected 2019 profile explicitly names the Lakshana Devi Temple at Bharmour as one of the four Chaurasi shrines under ASI Shimla Circle jurisdiction. ",
    "systematic_research_20261105_bharmour_manimahesh_chaurasi_asi_heritage_context":
        "The inspected 2019 profile explicitly names the Mani Mahesh Temple at Bharmour as one of the four Chaurasi shrines under ASI Shimla Circle jurisdiction. ",
    "systematic_research_20261105_bharmour_narsingh_chaurasi_asi_heritage_context":
        "The inspected 2019 profile explicitly names the Narasingha (catalogue: Narsingh) Temple at Bharmour as one of the four Chaurasi shrines under ASI Shimla Circle jurisdiction. ",
}


def main() -> None:
    docs = json.loads(DOCS.read_text(encoding="utf-8"))
    found = set()
    for doc in docs:
        prefix = TARGETS.get(doc.get("document_id"))
        if not prefix:
            continue
        marker = "A 2019 Government of India tourism-project profile"
        text = doc.get("text", "")
        if marker not in text:
            raise ValueError(f"Expected shared source text not found: {doc['document_id']}")
        if not text.startswith(prefix):
            text = prefix + text
            doc["text"] = text
            doc["content_hash"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        found.add(doc["document_id"])
    if found != set(TARGETS):
        raise ValueError(f"Missing expected documents: {sorted(set(TARGETS) - found)}")
    DOCS.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"documents_differentiated": len(found), "ids": sorted(found)}, indent=2))


if __name__ == "__main__":
    main()
