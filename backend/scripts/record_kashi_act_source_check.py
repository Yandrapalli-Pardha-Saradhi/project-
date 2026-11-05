import json
from datetime import datetime, timezone
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "data" / "research_plan_all_217.json"
plan = json.loads(path.read_text(encoding="utf-8"))
check = {
    "source_title": "The Uttar Pradesh Sri Kashi Vishwanath Temple Act, 1983 (officially hosted PDF)",
    "source_url": "https://shrikashivishwanath.org/files/adhiniyam_merged.pdf",
    "publisher": "Uttar Pradesh Legislature; document hosted on the Shri Kashi Vishwanath Temple site",
    "source_type": "state_temple_administration_act_pdf",
    "publication_date": "1983-10-13 (publication of English translation; amendments also appear in file)",
    "accessed_date": "2026-11-05",
    "inspection_method": "Opened and read statutory text defining the public worship temple and its administration; no automated collection.",
    "linked_temple_ids": ["kashi_vishwanath"],
    "categories_with_relevant_source_content": ["religious_cultural_significance"],
}
checks = plan.setdefault("source_checks_this_operation", [])
if not any(row.get("source_url") == check["source_url"] for row in checks):
    checks.append(check)
temple = next(row for row in plan["temples"] if row["temple_id"] == "kashi_vishwanath")
temple["sources_inspected"] = sorted(set(temple.get("sources_inspected", [])) | {check["source_url"]})
temple["categories_researched"] = sorted(set(temple.get("categories_researched", [])) | {"religious_cultural_significance"})
plan["last_updated_utc"] = datetime.now(timezone.utc).isoformat()
plan["temples_with_external_source_pages_inspected_this_operation"] = sum(bool(row.get("sources_inspected")) for row in plan["temples"])
plan["temples_not_yet_researched_this_operation"] = sum(not row.get("sources_inspected") for row in plan["temples"])
path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"source_pages_recorded": len(checks), "temples_with_pages_inspected": plan["temples_with_external_source_pages_inspected_this_operation"], "unresearched": plan["temples_not_yet_researched_this_operation"]}))
