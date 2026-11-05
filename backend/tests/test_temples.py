import json
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, HTTPException

from app.routes import temples as temple_routes
from app.routes.chat import chat, router as chat_router
from app.routes.temples import router as temples_router
from app.schemas.chat import ChatRequest


@pytest.fixture
def catalogue_file(tmp_path, monkeypatch):
    catalogue = [
        {"id": "shore", "names": ["Shore Temple", "Mamallapuram"], "alternate_names": ["Mahabalipuram Shore Temple"], "state": "Tamil Nadu", "district": "Chengalpattu", "area": "Mahabalipuram", "description": "Pallava monument.", "history": "Faces the Bay of Bengal.", "sources": [{"title": "Mahabalipuram", "url": "https://example.org/shore"}]},
        {"id": "konark", "names": ["Sun Temple at Konark"], "state": "Odisha", "district": "Puri", "area": "Konark", "description": "A temple to Surya.", "sources": [{"title": "Konark", "url": "https://example.org/konark"}]},
        {"id": "brihadeeswarar", "names": ["Brihadisvara Temple", "Big Temple"], "state": "Tamil Nadu", "district": "Thanjavur", "area": "Thanjavur", "description": "Chola temple.", "sources": []},
    ]
    path = tmp_path / "catalogue.json"
    path.write_text(json.dumps(catalogue), encoding="utf-8")
    monkeypatch.setattr(temple_routes, "CATALOGUE_PATH", path)
    return path


def test_routes_register_once_under_api_prefix():
    app = FastAPI()
    app.include_router(chat_router, prefix="/api")
    app.include_router(temples_router, prefix="/api")
    paths = app.openapi()["paths"]
    assert "/api/chat" in paths
    assert "/api/temples/states" in paths
    assert "/api/temples/facets" in paths
    assert "/api/temples/" in paths
    assert "/api/temples/{temple_id}" in paths
    router_paths = [route.path for route in temples_router.routes]
    assert router_paths.index("/temples/states") < router_paths.index("/temples/{temple_id}")


def test_states_and_listing(catalogue_file):
    states = temple_routes.get_temple_states()
    assert len(states) == 36
    assert "Odisha" in states and "Tamil Nadu" in states and "Puducherry" in states
    result = temple_routes.list_temples()
    assert result["total"] == 3
    assert len(result["items"]) == 3


@pytest.mark.parametrize("name,expected", [("mamallapuram", "shore"), ("Mahabalipuram Shore", "shore"), ("Big Temple", "brihadeeswarar")])
def test_search_matches_primary_and_alternative_names(catalogue_file, name, expected):
    result = temple_routes.list_temples(query=name)
    assert [item["id"] for item in result["items"]] == [expected]


def test_search_alias_partial_empty_and_pagination(catalogue_file):
    assert [item["id"] for item in temple_routes.list_temples(search="briha")["items"]] == ["brihadeeswarar"]
    assert temple_routes.list_temples(search="not a temple")["total"] == 0
    first = temple_routes.list_temples(limit=2, offset=0)
    second = temple_routes.list_temples(limit=2, offset=2)
    assert first["total"] == 3
    assert not ({item["id"] for item in first["items"]} & {item["id"] for item in second["items"]})
    assert len(first["items"] + second["items"]) == 3


def test_facets_are_scoped_to_real_catalogue_data(catalogue_file):
    facets = temple_routes.get_temple_facets(state="Tamil Nadu")
    assert facets["districts"] == ["Chengalpattu", "Thanjavur"]
    assert {item["id"] for item in facets["temples"]} == {"shore", "brihadeeswarar"}
    assert [item["id"] for item in temple_routes.list_temples(state="Tamil Nadu", district="Chengalpattu")["items"]] == ["shore"]
    assert temple_routes.get_temple_facets(state="Puducherry")["temples"] == []


@pytest.mark.parametrize("filters,expected", [({"state": "odisha"}, "konark"), ({"district": "Thanj"}, "brihadeeswarar"), ({"area": "Mahabalipuram"}, "shore")])
def test_location_filters(catalogue_file, filters, expected):
    result = temple_routes.list_temples(**filters)
    assert [item["id"] for item in result["items"]] == [expected]


def test_filters_combine_and_paginate(catalogue_file):
    result = temple_routes.list_temples(query="temple", state="Tamil Nadu", area="Thanjavur", limit=1)
    assert result["total"] == 1
    assert result["items"][0]["id"] == "brihadeeswarar"


def test_detail_and_unknown_id(catalogue_file):
    assert temple_routes.get_temple("shore")["history"] == "Faces the Bay of Bengal."
    with pytest.raises(HTTPException) as exc:
        temple_routes.get_temple("missing")
    assert exc.value.status_code == 404


@pytest.mark.parametrize("content", ["{broken", "{}"])
def test_malformed_catalogue_returns_503(catalogue_file, content):
    catalogue_file.write_text(content, encoding="utf-8")
    with pytest.raises(HTTPException) as exc:
        temple_routes.get_temple_states()
    assert exc.value.status_code == 503


def test_missing_catalogue_returns_503(catalogue_file):
    catalogue_file.unlink()
    with pytest.raises(HTTPException) as exc:
        temple_routes.list_temples()
    assert exc.value.status_code == 503


def test_chat_handler_regression():
    class FakeRag:
        def answer_question(self, **kwargs):
            return SimpleNamespace(answer="Grounded.", citations=[], language="en", insufficient_evidence=False, generation_disabled=True)

    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(rag_service=FakeRag())))
    result = chat(request, ChatRequest(question="Tell me about the temple", temple_id="shore"))
    assert result.answer == "Grounded."
    assert result.generation_disabled is True


def test_application_registers_discovery_and_health_routes():
    from app.main import app, health

    paths = app.openapi()["paths"]
    assert "/api/health" in paths
    assert "/api/chat" in paths
    assert "/api/temples/states" in paths
    assert "/api/temples/facets" in paths
    assert "/api/temples/" in paths
    assert "/api/temples/{temple_id}" in paths
    assert health()["status"] == "ok"


def test_expanded_catalogue_entries_have_linked_source_documents():
    from pathlib import Path

    backend_data = Path(__file__).resolve().parents[1] / "data"
    catalogue = json.loads((backend_data / "catalogue.json").read_text(encoding="utf-8"))
    documents = json.loads((backend_data / "raw" / "temple_sources.json").read_text(encoding="utf-8"))
    sources_by_id = {}
    for document in documents:
        sources_by_id.setdefault(document["temple_id"], []).append(document)
    assert len({item["id"] for item in catalogue}) == len(catalogue)
    assert len(catalogue) >= 100
    for temple in catalogue:
        source_documents = sources_by_id[temple["id"]]
        assert set(temple["document_ids"]) == {document["document_id"] for document in source_documents}
        assert isinstance(temple.get("description"), str) and temple["description"].strip()
        document_urls = {document["source_url"] for document in source_documents}
        assert all(source["url"] in document_urls for source in temple["sources"])
        assert all(document["temple_id"] == temple["id"] and document["source_url"].startswith("https://") for document in source_documents)
        assert isinstance(temple.get("district"), str) and temple["district"]
        if temple.get("location_source"):
            assert temple["location_source"]["url"].startswith("https://")


def test_expanded_catalogue_is_fully_returnable_across_pages():
    pages = [temple_routes.list_temples(limit=100, offset=offset) for offset in (0, 100, 200)]
    ids = [item["id"] for page in pages for item in page["items"]]
    assert pages[0]["total"] >= 100
    assert all(page["total"] == pages[0]["total"] for page in pages)
    assert len(ids) == pages[0]["total"]
    assert len(set(ids)) == pages[0]["total"]


def test_expanded_temple_search_and_location_filters_work_together():
    result = temple_routes.list_temples(search="ramappa", state="telangana", district="mulugu")
    assert result["total"] == 1
    temple = temple_routes.get_temple(result["items"][0]["id"])
    assert "Ramappa" in temple["canonical_name"]
    assert temple["area"] == "Palampet"


def test_similar_temple_names_open_distinct_catalogue_records():
    result = temple_routes.list_temples(search="virupaksha", state="Karnataka")
    assert result["total"] == 2
    details = [temple_routes.get_temple(item["id"]) for item in result["items"]]
    assert {item["area"] for item in details} == {"Hampi", "Pattadakal"}
