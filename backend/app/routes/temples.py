from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query

from app.config import DATA_DIR

logger = logging.getLogger("temple_heritage.temples")
router = APIRouter()
CATALOGUE_PATH = DATA_DIR / "catalogue.json"

# National selector options are intentionally distinct from the places represented
# in this curated catalogue. Source: National Portal of India, State/UT directory.
INDIAN_STATES_AND_UTS = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands",
    "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Lakshadweep", "Puducherry",
]


def _load_catalogue() -> list[dict[str, Any]]:
    try:
        with CATALOGUE_PATH.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, list):
            raise ValueError("catalogue root must be a JSON array")
        seen: set[str] = set()
        for index, item in enumerate(data):
            if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].strip():
                raise ValueError(f"catalogue entry {index} has no valid id")
            if item["id"] in seen:
                raise ValueError(f"duplicate temple id: {item['id']}")
            if not isinstance(item.get("names"), list) or not item["names"] or not all(isinstance(n, str) for n in item["names"]):
                raise ValueError(f"catalogue entry {item['id']} has invalid names")
            if not isinstance(item.get("sources", []), list):
                raise ValueError(f"catalogue entry {item['id']} has invalid sources")
            seen.add(item["id"])
        return data
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        logger.error("Temple catalogue unavailable or invalid at %s: %s", CATALOGUE_PATH, exc)
        raise HTTPException(status_code=503, detail="Temple catalogue is unavailable") from exc


def _matches(value: str | None, filter_value: str) -> bool:
    return bool(value and filter_value.casefold() in value.casefold())


def _summary(temple: dict[str, Any]) -> dict[str, Any]:
    return {key: temple.get(key) for key in ("id", "names", "state", "district", "area", "description", "sources", "location_source")}


@router.get("/temples/states", response_model=list[str])
def get_temple_states() -> list[str]:
    _load_catalogue()  # Validate availability before returning selector options.
    return INDIAN_STATES_AND_UTS.copy()


@router.get("/temples/facets")
def get_temple_facets(
    state: Annotated[str, Query(max_length=100)] = "",
    district: Annotated[str, Query(max_length=100)] = "",
) -> dict[str, Any]:
    temples = _load_catalogue()
    filtered = [
        temple for temple in temples
        if (not state or (temple.get("state") or "").casefold() == state.casefold())
        and (not district or (temple.get("district") or "").casefold() == district.casefold())
    ]
    districts = sorted({t["district"] for t in filtered if isinstance(t.get("district"), str) and t["district"].strip()})
    return {"districts": districts, "temples": [_summary(t) for t in filtered]}


@router.get("/temples/")
def list_temples(
    query: Annotated[str, Query(max_length=120)] = "",
    search: Annotated[str, Query(max_length=120)] = "",
    state: Annotated[str, Query(max_length=100)] = "",
    district: Annotated[str, Query(max_length=100)] = "",
    area: Annotated[str, Query(max_length=100)] = "",
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    temples = _load_catalogue()
    query = search or query
    filtered = []
    for temple in temples:
        if state and not _matches(temple.get("state"), state):
            continue
        if district and not _matches(temple.get("district"), district):
            continue
        if area and not _matches(temple.get("area"), area):
            continue
        names = [*temple.get("names", []), *temple.get("alternate_names", [])]
        if query and not any(_matches(name, query) for name in names):
            continue
        filtered.append(temple)
    filtered.sort(key=lambda item: item["names"][0].casefold())
    return {"items": [_summary(t) for t in filtered[offset:offset + limit]], "total": len(filtered), "limit": limit, "offset": offset}


@router.get("/temples/{temple_id}")
def get_temple(temple_id: str) -> dict[str, Any]:
    temple = next((item for item in _load_catalogue() if item["id"] == temple_id), None)
    if temple is None:
        raise HTTPException(status_code=404, detail="Temple not found")
    return temple
