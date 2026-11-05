"""Record a researched same-name mismatch without attaching false evidence."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1] / "data" / "research_plan_all_217.json"
TEMPLE_ID = "asi_himachal_pra_dddb6f1b1b3e3ef2"
URL = "https://himachaltourism.gov.in/destination/temples/"


def main() -> None:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    attempts = plan.setdefault("inaccessible_or_unmapped_source_attempts", [])
    key = (TEMPLE_ID, URL)
    if not any((x.get("linked_temple_ids") == [TEMPLE_ID] and x.get("source_url") == URL) for x in attempts):
        attempts.append({
            "attempt_id": "systematic_research_20261105_trilokinath_locality_mismatch",
            "temple_id": TEMPLE_ID,
            "linked_temple_ids": [TEMPLE_ID],
            "temple_name": "Temple of Trillokinath",
            "source_url": URL,
            "result": "unmapped_identity_mismatch",
            "attempted_at_utc": datetime.now(timezone.utc).isoformat(),
            "note": "The inspected official Himachal Tourism page discusses a Trilokinath Temple at Udaipur in Lahaul-Spiti, while this catalogue record is localized to Mandi. No supporting evidence establishes that the records identify the same site, so no facts or citation were attached. Research this catalogue identity separately.",
        })
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Recorded locality mismatch; source not attached to the catalogue temple.")


if __name__ == "__main__":
    main()
