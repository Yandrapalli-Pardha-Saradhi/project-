from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import SUPPORTED_LANGUAGES
from app.schemas.chat import ChatRequest, Citation, ConversationMessage
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.rag_service import RAGResult, RAGService
from app.services.retrieval_service import RetrievedChunk, RetrievalService
from app.services.web_search_service import WebSearchResult
from app.routes.chat import router as chat_router


class FixedEmbeddingService(EmbeddingService):
    """Deterministic, network-free embeddings for tests.

    Maps each text to a pre-defined vector so retrieval ordering and distances
    are fully predictable without downloading any model.
    """

    def __init__(self, vectors: dict[str, list[float]]):
        self.vectors = vectors
        self.model_name = "fixed-test-embedding"
        self._model = None

    def _vector_for(self, text: str) -> list[float]:
        if text in self.vectors:
            return self.vectors[text]
        # Deterministic fallback for texts not in the table (e.g. user queries).
        vec = [0.0] * self.dim
        for i, ch in enumerate(text.lower()):
            vec[i % self.dim] += (ord(ch) % 5) / 5.0
        norm = sum(x * x for x in vec) ** 0.5 or 1.0
        return [x / norm for x in vec]

    def embed_texts(self, texts):  # type: ignore[override]
        return [self._vector_for(t) for t in texts]

    def embed_query(self, text):  # type: ignore[override]
        return self._vector_for(text)


class FakeLLMService(LLMService):
    def __init__(self, response_text: str = "", enabled: bool = True):
        self.response_text = response_text
        self.enabled = enabled
        self.calls = []

    @property
    def is_enabled(self) -> bool:
        return self.enabled

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        self.calls.append((system_prompt, user_prompt, temperature))
        return self.response_text


DOC1_TEXT = "The Brihadisvara Temple at Thanjavur was built by Rajaraja I in the 11th century CE."
DOC2_TEXT = "Granite for the temple was transported from quarries about 50 kilometres away."
DOC3_TEXT = "The Sun Temple at Konark was built in the 13th century as a stone chariot for Surya."

ORTHONORMAL_VECTORS = {
    DOC1_TEXT: [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    DOC2_TEXT: [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    DOC3_TEXT: [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
}

SAMPLE_DOCS = [
    {
        "id": "brihadeeswarar_001_chunk_0",
        "text": DOC1_TEXT,
        "metadata": {
            "document_id": "brihadeeswarar_001",
            "temple_id": "brihadeeswarar",
            "source_title": "Great Living Chola Temples",
            "source_url": "https://whc.unesco.org/en/list/250/",
            "publisher": "UNESCO World Heritage Centre",
            "is_paraphrase": True,
            "chunk_index": 0,
            "state": "Tamil Nadu",
            "district": "Thanjavur",
        },
    },
    {
        "id": "brihadeeswarar_002_chunk_0",
        "text": DOC2_TEXT,
        "metadata": {
            "document_id": "brihadeeswarar_002",
            "temple_id": "brihadeeswarar",
            "source_title": "Great Living Chola Temples",
            "source_url": "https://whc.unesco.org/en/list/250/",
            "publisher": "UNESCO World Heritage Centre",
            "is_paraphrase": True,
            "chunk_index": 0,
            "state": "Tamil Nadu",
            "district": "Thanjavur",
        },
    },
    {
        "id": "konark_001_chunk_0",
        "text": DOC3_TEXT,
        "metadata": {
            "document_id": "konark_001",
            "temple_id": "konark",
            "source_title": "Sun Temple, Konârak",
            "source_url": "https://whc.unesco.org/en/list/246/",
            "publisher": "UNESCO World Heritage Centre",
            "is_paraphrase": True,
            "chunk_index": 0,
            "state": "Odisha",
            "district": "Puri",
        },
    },
]


def make_retrieval_service(tmp_path, docs, embedding_service=None):
    if embedding_service is None:
        embedding_service = FixedEmbeddingService(ORTHONORMAL_VECTORS)
    service = RetrievalService(
        embedding_service, str(tmp_path / "chroma"), "test_collection"
    )
    if docs:
        ids = [d["id"] for d in docs]
        texts = [d["text"] for d in docs]
        metadatas = [d["metadata"] for d in docs]
        embeddings = embedding_service.embed_texts(texts)
        service.collection.upsert(
            ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings
        )
    return service


def make_rag_service(
    tmp_path,
    docs=None,
    llm_response="",
    llm_enabled=True,
    top_k=5,
    threshold=0.7,
    embedding_service=None,
):
    retrieval_service = make_retrieval_service(
        tmp_path, docs or [], embedding_service=embedding_service
    )
    llm_service = FakeLLMService(response_text=llm_response, enabled=llm_enabled)
    settings = SimpleNamespace(top_k=top_k, relevance_threshold=threshold)
    return RAGService(settings, retrieval_service, llm_service)


def make_test_app(rag_service):
    app = FastAPI()
    app.include_router(chat_router, prefix="/api")
    app.state.rag_service = rag_service
    return app


import json  # noqa: E402  (file was split; used below)


# ---------------------------------------------------------------------------
# RAG tests
# ---------------------------------------------------------------------------


LLM_ANSWER = (
    "The Brihadisvara Temple was built by Rajaraja I in the 11th century CE. "
    "[brihadeeswarar_001_chunk_0]"
)
LLM_JSON = json.dumps(
    {
        "answer": LLM_ANSWER,
        "cited_chunk_ids": ["brihadeeswarar_001_chunk_0"],
    }
)


def test_citations_map_to_actual_stored_urls(tmp_path):
    # The user query is embedded like DOC1 so it is the top relevant result.
    vectors = dict(ORTHONORMAL_VECTORS)
    vectors["Who built the Brihadisvara Temple?"] = ORTHONORMAL_VECTORS[DOC1_TEXT]
    embedding_service = FixedEmbeddingService(vectors)
    rag = make_rag_service(
        tmp_path,
        docs=SAMPLE_DOCS,
        llm_response=LLM_JSON,
        threshold=0.7,
        embedding_service=embedding_service,
    )
    result = rag.answer_question("Who built the Brihadisvara Temple?", language="en")

    assert result.insufficient_evidence is False
    assert result.generation_disabled is False
    assert len(result.citations) == 1
    citation = result.citations[0]
    assert citation.source_id == "brihadeeswarar_001"
    assert citation.source_title == "Great Living Chola Temples"
    assert citation.source_url == "https://whc.unesco.org/en/list/250/"
    assert citation.publisher == "UNESCO World Heritage Centre"
    assert citation.excerpt == DOC1_TEXT


def test_hallucinated_citation_ids_are_rejected(tmp_path):
    vectors = dict(ORTHONORMAL_VECTORS)
    vectors["Who built the Brihadisvara Temple?"] = ORTHONORMAL_VECTORS[DOC1_TEXT]
    embedding_service = FixedEmbeddingService(vectors)
    rag = make_rag_service(
        tmp_path,
        docs=SAMPLE_DOCS,
        llm_response=json.dumps(
            {
                "answer": "Some answer [brihadeeswarar_001_chunk_0] and a fake source.",
                "cited_chunk_ids": ["brihadeeswarar_001_chunk_0", "made_up_chunk_9"],
            }
        ),
        threshold=0.7,
        embedding_service=embedding_service,
    )
    result = rag.answer_question("Who built the Brihadisvara Temple?", language="en")

    assert len(result.citations) == 1
    assert result.citations[0].source_id == "brihadeeswarar_001"
    assert all(c.source_url.startswith("https://whc.unesco.org/") for c in result.citations)


def test_insufficient_evidence_when_nothing_relevant(tmp_path):
    orthogonal_query = "this query matches nothing in the collection"
    vectors = dict(ORTHONORMAL_VECTORS)
    vectors[orthogonal_query] = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
    embedding_service = FixedEmbeddingService(vectors)

    rag = make_rag_service(
        tmp_path,
        docs=SAMPLE_DOCS,
        llm_enabled=True,
        threshold=0.7,
        embedding_service=embedding_service,
    )
    result = rag.answer_question(orthogonal_query, language="en")

    assert result.insufficient_evidence is True
    assert result.generation_disabled is False
    assert result.citations == []
    assert "sufficient reliable evidence" in result.answer.lower()


def test_insufficient_evidence_on_empty_collection(tmp_path):
    rag = make_rag_service(tmp_path, docs=[], llm_enabled=True, threshold=0.7)
    result = rag.answer_question("Anything at all", language="en")

    assert result.insufficient_evidence is True
    assert result.citations == []
    assert result.generation_disabled is False


def test_catalogue_only_inventory_evidence_does_not_supply_an_unstated_date():
    text = (
        "The ASI inventory records Ramappa temple in Palampet, Mulugu district, Telangana. "
        "The inventory does not state a construction date, deity, architectural style, or festival."
    )
    chunk = RetrievedChunk("asi_inventory_chunk_0", text, 0.1, {
        "document_id": "asi_inventory_ramappa",
        "temple_id": "asi_telangana_f3a7458053e48f24",
        "source_title": "Centrally Protected Monuments/Sites: State-wise and Circle-wise",
        "source_url": "https://asi.nic.in/pdf/CPM_List.pdf",
        "publisher": "Archaeological Survey of India",
    })
    retrieval = SpyRetrievalService([chunk])
    rag = make_spy_rag(retrieval, FakeLLMService(enabled=False))
    result = rag.answer_question(
        "What construction year does the inventory give?",
        temple_id="asi_telangana_f3a7458053e48f24",
    )
    assert result.insufficient_evidence is True
    assert "sufficient reliable evidence" in result.answer.lower()
    assert not any(year in result.answer for year in ("1200", "1213", "13th century"))
    assert result.citations == []


def test_food_small_talk_does_not_run_heritage_retrieval(tmp_path):
    rag = make_rag_service(tmp_path, docs=[])
    def unexpected_retrieval(*args, **kwargs):
        raise AssertionError("small talk should not query the heritage index")
    rag.retrieval_service.retrieve = unexpected_retrieval
    result = rag.answer_question("so do u think idly is good or bad")
    assert "taste is personal" in result.answer.lower()
    assert "heritage" in result.answer
    assert result.citations == []
    assert result.insufficient_evidence is False


def test_food_small_talk_does_not_retrieve_inside_temple_scoped_conversation(tmp_path):
    rag = make_rag_service(tmp_path, docs=[])
    def unexpected_retrieval(*args, **kwargs):
        raise AssertionError("off-topic small talk should not query the heritage index")
    rag.retrieval_service.retrieve = unexpected_retrieval
    history = [
        ConversationMessage(role="user", content="Tell me about Brihadeeswarar Temple"),
        ConversationMessage(role="assistant", content="A Chola temple.", context_temple_id="brihadeeswarar"),
    ]
    result = rag.answer_question("Is idli good or bad?", temple_id="brihadeeswarar", history=history)
    assert result.citations == []
    assert result.context_temple_id is None


def test_food_word_in_heritage_question_still_uses_rag(tmp_path):
    rag = make_rag_service(tmp_path, docs=[])
    result = rag.answer_question("What food offering is associated with Jagannath Temple?")
    assert result.insufficient_evidence is True


def test_retrieval_only_mode_without_llm_key(tmp_path):
    vectors = dict(ORTHONORMAL_VECTORS)
    vectors["Who built the Brihadisvara Temple?"] = ORTHONORMAL_VECTORS[DOC1_TEXT]
    embedding_service = FixedEmbeddingService(vectors)
    rag = make_rag_service(
        tmp_path,
        docs=SAMPLE_DOCS,
        llm_enabled=False,
        threshold=0.7,
        embedding_service=embedding_service,
    )
    result = rag.answer_question("Who built the Brihadisvara Temple?", language="en")

    assert result.insufficient_evidence is False
    assert result.generation_disabled is True
    assert "not configured" in result.answer.lower()
    assert len(result.citations) == 1
    assert result.citations[0].source_url == "https://whc.unesco.org/en/list/250/"


def test_unsupported_language_raises(tmp_path):
    rag = make_rag_service(tmp_path, docs=SAMPLE_DOCS, llm_enabled=False)
    with pytest.raises(ValueError):
        rag.answer_question("Who built the temple?", language="fr")

# ---------------------------------------------------------------------------
# API tests (LLM calls are faked; no API key or network required)
# ---------------------------------------------------------------------------


FAKE_RAG_RESULT = RAGResult(
    answer="Generated answer.",
    citations=[
        Citation(
            source_id="brihadeeswarar_001",
            source_title="Great Living Chola Temples",
            source_url="https://whc.unesco.org/en/list/250/",
            publisher="UNESCO World Heritage Centre",
            excerpt="excerpt text",
        )
    ],
    language="en",
    insufficient_evidence=False,
    generation_disabled=True,
)


class FakeRAGServiceForAPI:
    def answer_question(self, question: str, language: str = "en", temple_id=None, history=None):
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{language}'. Supported: {', '.join(SUPPORTED_LANGUAGES)}"
            )
        return RAGResult(
            answer="Generated answer.",
            citations=[
                Citation(
                    source_id="brihadeeswarar_001",
                    source_title="Great Living Chola Temples",
                    source_url="https://whc.unesco.org/en/list/250/",
                    publisher="UNESCO World Heritage Centre",
                    excerpt="excerpt text",
                )
            ],
            language=language,
            insufficient_evidence=False,
            generation_disabled=True,
        )


def test_api_missing_question_is_rejected():
    app = make_test_app(FakeRAGServiceForAPI())
    client = TestClient(app)
    response = client.post("/api/chat", json={})
    assert response.status_code == 422


def test_api_empty_question_is_rejected():
    app = make_test_app(FakeRAGServiceForAPI())
    client = TestClient(app)
    response = client.post("/api/chat", json={"question": "   "})
    assert response.status_code == 422


def test_api_invalid_language_is_rejected():
    app = make_test_app(FakeRAGServiceForAPI())
    client = TestClient(app)
    response = client.post(
        "/api/chat", json={"question": "Who built the temple?", "language": "fr"}
    )
    assert response.status_code == 422


def test_api_valid_request_returns_consistent_shape():
    app = make_test_app(FakeRAGServiceForAPI())
    client = TestClient(app)
    response = client.post(
        "/api/chat",
        json={
            "question": "Who built the temple?",
            "language": "te",
            "temple_id": "brihadeeswarar",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Generated answer."
    assert body["language"] == "te"
    assert body["insufficient_evidence"] is False
    assert body["generation_disabled"] is True
    assert len(body["citations"]) == 1
    citation = body["citations"][0]
    assert citation["source_id"] == "brihadeeswarar_001"
    assert citation["source_title"] == "Great Living Chola Temples"
    assert citation["source_url"] == "https://whc.unesco.org/en/list/250/"
    assert citation["publisher"] == "UNESCO World Heritage Centre"
    assert citation["excerpt"] == "excerpt text"

# ---------------------------------------------------------------------------
# Retrieval tests
# ---------------------------------------------------------------------------


def test_retrieval_returns_top_chunks_with_distances_and_metadata(tmp_path):
    service = make_retrieval_service(tmp_path, SAMPLE_DOCS)
    assert service.count() == 3
    results = service.retrieve(DOC1_TEXT, top_k=5)

    assert len(results) == 3
    distances = [result.distance for result in results]
    assert distances == sorted(distances)
    assert distances[0] == 0.0
    assert results[0].chunk_id == "brihadeeswarar_001_chunk_0"
    assert results[0].metadata["source_url"] == "https://whc.unesco.org/en/list/250/"


def test_retrieval_respects_temple_filter(tmp_path):
    service = make_retrieval_service(tmp_path, SAMPLE_DOCS)
    results = service.retrieve(DOC1_TEXT, top_k=5, temple_id="konark")

    assert len(results) == 1
    assert results[0].chunk_id == "konark_001_chunk_0"
    assert results[0].metadata["temple_id"] == "konark"


def test_retrieval_respects_state_and_district_filters(tmp_path):
    service = make_retrieval_service(tmp_path, SAMPLE_DOCS)
    state_results = service.retrieve(DOC1_TEXT, top_k=5, state="Odisha")
    district_results = service.retrieve(DOC1_TEXT, top_k=5, state="Tamil Nadu", district="Thanjavur")
    assert [result.metadata["temple_id"] for result in state_results] == ["konark"]
    assert [result.metadata["temple_id"] for result in district_results] == ["brihadeeswarar", "brihadeeswarar"]


def test_retrieval_on_empty_collection_returns_nothing(tmp_path):
    service = make_retrieval_service(tmp_path, [])
    assert service.count() == 0
    assert service.retrieve(DOC1_TEXT, top_k=5) == []


class SpyRetrievalService:
    def __init__(self, chunks=None):
        self.chunks = chunks or []
        self.calls = []

    def retrieve(self, query, top_k=5, temple_id=None):
        self.calls.append((query, top_k, temple_id))
        return self.chunks


def make_spy_rag(retrieval, llm=None, threshold=0.7):
    return RAGService(
        SimpleNamespace(top_k=5, relevance_threshold=threshold),
        retrieval,
        llm or FakeLLMService(response_text=LLM_JSON),
    )


@pytest.mark.parametrize("greeting", ["hi", "hii", "hello", "good morning", "Namaste!"])
def test_greetings_bypass_retrieval_and_return_a_friendly_invitation(greeting):
    retrieval = SpyRetrievalService()
    rag = make_spy_rag(retrieval)
    result = rag.answer_question(greeting)
    assert retrieval.calls == []
    assert result.insufficient_evidence is False
    assert result.citations == []
    assert "temples and heritage" in result.answer


def test_follow_up_uses_prior_temple_scope_and_bounded_context():
    chunk = RetrievedChunk(
        "brihadeeswarar_001_chunk_0", DOC1_TEXT, 0.1, SAMPLE_DOCS[0]["metadata"]
    )
    retrieval = SpyRetrievalService([chunk])
    llm = FakeLLMService(response_text=LLM_JSON)
    rag = make_spy_rag(retrieval, llm)
    history = [
        ConversationMessage(role="user", content="what is brihadeeswar temple"),
        ConversationMessage(role="assistant", content="It is a Chola temple."),
    ]
    result = rag.answer_question(
        "what is special about this temple", history=history, temple_id="brihadeeswarar"
    )
    query, _, temple_id = retrieval.calls[0]
    assert temple_id == "brihadeeswarar"
    assert "Brihadisvara Temple" in query
    assert "what is brihadeeswar temple" not in query
    assert "what is brihadeeswar temple" in llm.calls[0][1]
    assert result.context_temple_id == "brihadeeswarar"
    assert all(citation.source_url.endswith("/250/") for citation in result.citations)


def test_generic_follow_up_words_do_not_override_selected_temple_context():
    rag = make_spy_rag(SpyRetrievalService())
    history = [
        ConversationMessage(role="user", content="Tell me about Pattabhirama Temple."),
        ConversationMessage(
            role="assistant", content="Here is the temple overview.",
            context_temple_id="whc_5a482f12eb769406674c",
        ),
    ]
    assert rag._resolve_temple_context(
        "What about the construction date and its layout?", history, None
    ) == "whc_5a482f12eb769406674c"


def test_question_name_resolves_typo_and_changes_previous_temple():
    retrieval = SpyRetrievalService()
    rag = make_spy_rag(retrieval)
    assert rag._resolve_temple_context("what is brihadeeswar temple", [], None) == "brihadeeswarar"
    history = [
        ConversationMessage(role="user", content="What is Brihadeeswar Temple?"),
        ConversationMessage(role="assistant", content="A temple in Thanjavur."),
    ]
    result = rag.answer_question("Tell me about Konark Sun Temple", history=history)
    assert retrieval.calls[0][2] == "konark"
    assert result.context_temple_id == "konark"


@pytest.mark.parametrize("question,expected_id", [
    ("What architectural features are highlighted about Ramappa temple?", "asi_telangana_f3a7458053e48f24"),
    ("What is distinctive about the Vitthala complex?", "whc_0601b84399076df5f6eb"),
    ("What is the Mahabodhi temple associated with?", "whc_b64d0b1bb2989639c1f1"),
    ("What period and dynasty are associated with Khajuraho temples?", "whc_798b3d431ca45563a0f8"),
    ("How did Pattadakal combine architectural styles?", "asi_karnataka_7c32bc783d1664dc"),
])
def test_expanded_temple_names_resolve_without_generic_word_collisions(question, expected_id):
    rag = make_spy_rag(SpyRetrievalService())
    assert rag._mentioned_temple_ids(question) == [expected_id]


@pytest.mark.parametrize("question,expected_id", [
    ("Tell me about Bisdol (Bishnudol) (Gaurisagar)", "asi_assam_3176178449463d6c"),
    ("Tell me about Devidol (Gaurisagar)", "asi_assam_d296790c660bb3b9"),
    ("Tell me about Sivadol (Gaurisagar)", "asi_assam_150626777a56d77d"),
    ("Tell me about Mallikarjuna (Siva) temple", "asi_andhra_prade_5509b425f6edbf42"),
])
def test_longer_exact_temple_name_disambiguates_shared_aliases(question, expected_id):
    rag = make_spy_rag(SpyRetrievalService())
    rag._temples = json.loads(
        (Path(__file__).parents[1] / "data" / "catalogue.json").read_text(encoding="utf-8")
    )
    assert rag._mentioned_temple_ids(question) == [expected_id]


def test_shared_short_temple_alias_remains_ambiguous():
    rag = make_spy_rag(SpyRetrievalService())
    rag._temples = json.loads(
        (Path(__file__).parents[1] / "data" / "catalogue.json").read_text(encoding="utf-8")
    )
    assert set(rag._mentioned_temple_ids("Tell me about Devidol")) == {
        "asi_assam_d296790c660bb3b9",
        "asi_assam_6f13d020bbaf4068",
    }


def test_world_heritage_group_name_is_not_misresolved_to_an_individual_temple():
    rag = make_spy_rag(SpyRetrievalService())
    assert rag._mentioned_temple_ids("Which temples comprise the Great Living Chola Temples?") == []


def test_comparison_is_not_accidentally_scoped_to_prior_temple():
    retrieval = SpyRetrievalService()
    rag = make_spy_rag(retrieval)
    rag.answer_question("Compare this temple with Konark Sun Temple", temple_id="brihadeeswarar")
    assert retrieval.calls[0][2] is None


def test_explicitly_cleared_context_does_not_return_from_older_history():
    rag = make_spy_rag(SpyRetrievalService())
    history = [
        ConversationMessage(role="user", content="What is Brihadeeswar Temple?"),
        ConversationMessage(role="assistant", content="A Chola temple.", context_temple_id=None),
    ]
    assert rag._resolve_temple_context("tell me more", history, None) is None


def test_explicit_new_heritage_topic_clears_previous_temple_scope():
    rag = make_spy_rag(SpyRetrievalService())
    assert rag._resolve_temple_context("Explain the Chola dynasty", [], "brihadeeswarar") is None


def test_irrelevant_retrieval_is_rejected_without_calling_llm():
    chunk = RetrievedChunk("irrelevant_chunk_0", "Unrelated text.", 0.95, SAMPLE_DOCS[0]["metadata"])
    retrieval = SpyRetrievalService([chunk])
    llm = FakeLLMService(response_text=LLM_JSON)
    result = make_spy_rag(retrieval, llm, threshold=0.7).answer_question("A question")
    assert result.insufficient_evidence is True
    assert result.citations == []
    assert llm.calls == []
    assert "sufficient reliable evidence" in result.answer


def test_festival_question_drops_relevant_scored_but_nonfestival_temple_passage():
    chunk = RetrievedChunk(
        "inventory_chunk_0",
        "The ASI inventory lists the temple in the village and district. It provides no festival information.",
        0.1,
        {"document_id": "inventory", "temple_id": "brihadeeswarar", "topic": "asi_inventory_listing",
         "source_url": "https://asi.nic.in/pdf/CPM_List.pdf"},
    )
    retrieval = SpyRetrievalService([chunk])
    llm = FakeLLMService(response_text=LLM_JSON)
    result = make_spy_rag(retrieval, llm).answer_question(
        "What festivals are held there?", temple_id="brihadeeswarar"
    )
    assert result.insufficient_evidence is True
    assert result.citations == []
    assert llm.calls == []


def test_topic_filter_keeps_matching_architecture_evidence():
    architecture = RetrievedChunk(
        "architecture_chunk_0",
        "The vimana rises above the sanctum and the mandapa has carved stone pillars.",
        0.1,
        {"document_id": "architecture", "temple_id": "brihadeeswarar", "topic": "architecture",
         "source_url": "https://whc.unesco.org/en/list/250/"},
    )
    inventory = RetrievedChunk(
        "inventory_chunk_0", "The inventory lists the monument and its locality.", 0.1,
        {"document_id": "inventory", "temple_id": "brihadeeswarar", "topic": "asi_inventory_listing"},
    )
    selected = RAGService._filter_to_requested_topics("Describe its architecture", [architecture, inventory])
    assert selected == [architecture]


def test_world_heritage_inscription_is_not_temple_epigraphic_evidence():
    assert not RAGService._text_has_positive_topic_evidence(
        "The UNESCO decision identifies the temple as one component of the inscribed serial property.",
        "inscriptions_historical_evidence",
    )
    assert RAGService._text_has_positive_topic_evidence(
        "Temple inscriptions record gifts made by the ruler, and an epigraphic study identifies the script.",
        "inscriptions_historical_evidence",
    )
    assert RAGService._text_has_positive_topic_evidence(
        "The front mandapa is identified in inscriptions as Rajagambhiran tirumandapam.",
        "inscriptions_historical_evidence",
    )
    assert not RAGService._text_has_positive_topic_evidence(
        "This tourism account distinguishes its description from independently reviewed epigraphic evidence.",
        "inscriptions_historical_evidence",
    )
    assert RAGService._requested_topic_categories(
        "What inscriptions, scripts, grants or epigraphic records are documented for the temple?"
    ) == {"inscriptions_historical_evidence"}


def test_conservation_history_does_not_open_general_history_context():
    assert RAGService._requested_topic_categories(
        "What heritage status or conservation history is documented for the temple?"
    ) == {"heritage_conservation"}
    archive_index = (
        "The Assam State Archives index lists a 1925 file titled Preservation of the mound. "
        "The index entry alone does not reveal what work was proposed or completed, and it is "
        "not evidence of the monument's current condition or protection status."
    )
    assert not RAGService._text_has_positive_topic_evidence(
        archive_index, "heritage_conservation"
    )


def test_historical_topic_gate_accepts_documented_commission_date_and_patron():
    chunk = RetrievedChunk(
        "history_chunk_0",
        "The dossier says merchant Kullahana Rahuta and his wife Sajajadevi commissioned the temple in 1113 CE.",
        0.1,
        {"document_id": "history", "temple_id": "lakshmidevi", "topic": "historical_background"},
    )
    assert RAGService._chunk_supports_topic(chunk, "historical_background")


def test_multi_topic_question_refuses_when_one_requested_topic_has_no_evidence():
    history = RetrievedChunk(
        "history_chunk_0", "The shrine was built in the 12th century by a local ruler.", 0.1,
        {"document_id": "history", "temple_id": "brihadeeswarar", "topic": "historical_background"},
    )
    assert RAGService._filter_to_requested_topics(
        "Explain the history and festivals", [history]
    ) == []


def test_temple_scope_drops_unrelated_passages_even_if_returned_by_adapter():
    brih_chunk = RetrievedChunk(
        "brihadeeswarar_001_chunk_0", DOC1_TEXT, 0.1, SAMPLE_DOCS[0]["metadata"]
    )
    konark_chunk = RetrievedChunk(
        "konark_001_chunk_0", DOC3_TEXT, 0.1, SAMPLE_DOCS[2]["metadata"]
    )
    retrieval = SpyRetrievalService([brih_chunk, konark_chunk])
    llm = FakeLLMService(response_text=LLM_JSON)
    result = make_spy_rag(retrieval, llm).answer_question(
        "what is special about this temple", temple_id="brihadeeswarar"
    )
    assert len(llm.calls) == 1
    assert "Konark" not in llm.calls[0][1]
    assert all(citation.source_id.startswith("brihadeeswarar") for citation in result.citations)


def test_citations_are_unique_by_source_url():
    first = RetrievedChunk("first_chunk_0", "Evidence one.", 0.1, {
        "document_id": "source_one", "source_title": "Shared source", "source_url": "https://example.org/source"
    })
    second = RetrievedChunk("second_chunk_0", "Evidence two.", 0.1, {
        "document_id": "source_two", "source_title": "Shared source", "source_url": "https://example.org/source"
    })
    citations = RAGService._build_citations([first, second])
    assert len(citations) == 1
    assert citations[0].source_id == "source_one"


def test_citation_deduplication_normalizes_trailing_slashes():
    from app.schemas.chat import Citation

    citations = RAGService._dedupe_citations([
        Citation(source_id="one", source_title="UNESCO", source_url="https://whc.unesco.org/en/list/250", excerpt="first"),
        Citation(source_id="two", source_title="UNESCO", source_url="https://whc.unesco.org/en/list/250/", excerpt="second"),
    ])
    assert len(citations) == 1


def test_web_fallback_only_returns_cited_real_sources():
    class FakeWebSearch:
        enabled = True

        def search(self, query, max_results=3):
            return [
                WebSearchResult("Unused page", "https://example.org/unused", "Unused snippet", "Example"),
                WebSearchResult("Used page", "https://example.org/used", "Used snippet", "Example"),
            ]

    retrieval = SpyRetrievalService()
    llm = FakeLLMService(response_text=json.dumps({
        "answer": "This answer uses the second source [web_1]",
        "cited_chunk_ids": ["web_1", "not-a-source"],
    }))
    rag = RAGService(
        SimpleNamespace(top_k=5, relevance_threshold=0.7), retrieval, llm, FakeWebSearch()
    )
    result = rag.answer_question("A question without local evidence")
    assert result.answer == "This answer uses the second source"
    assert [citation.source_url for citation in result.citations] == ["https://example.org/used"]


def test_history_validation_requires_bounded_complete_turns():
    with pytest.raises(Exception):
        ChatRequest(question="Follow up", history=[{"role": "user", "content": "Hi"}])
    with pytest.raises(Exception):
        ChatRequest(question="Follow up", history=[
            {"role": "user", "content": "Hi"}, {"role": "user", "content": "Again"}
        ])
    with pytest.raises(Exception):
        ChatRequest(question="Follow up", history=[
            {"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": "1"}, {"role": "assistant", "content": "2"},
            {"role": "user", "content": "3"}, {"role": "assistant", "content": "4"},
            {"role": "user", "content": "5"}, {"role": "assistant", "content": "6"},
            {"role": "user", "content": "too many"}, {"role": "assistant", "content": "turns"},
        ])
