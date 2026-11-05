from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.retrieval_service import RetrievalService
from app.services.web_search_service import WebSearchService
from app.routes.chat import router as chat_router
from app.routes.temples import router as temples_router

settings = Settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)

# CORS: never allow unrestricted origins in production. Origins must be
# explicitly configured via CORS_ORIGINS; a wildcard is only tolerated in debug.
configured_origins = settings.cors_origins_list
if settings.debug and not configured_origins:
    allow_origins: list[str] = ["*"]
    allow_credentials = False
else:
    allow_origins = configured_origins
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

embedding_service = EmbeddingService(settings.embedding_model)
retrieval_service = RetrievalService(
    embedding_service, settings.chroma_persist_dir, settings.collection_name
)
llm_api_key = settings.llm_api_key.get_secret_value() if settings.llm_api_key else None
llm_service = LLMService(settings.llm_base_url, llm_api_key, settings.llm_model)
web_search_service = WebSearchService(
    enabled=settings.web_search_enabled,
    timeout=settings.web_search_timeout,
)
rag_service = RAGService(settings, retrieval_service, llm_service, web_search_service)

app.state.rag_service = rag_service
app.state.embedding_service = embedding_service
app.state.retrieval_service = retrieval_service
app.state.llm_service = llm_service
app.state.web_search_service = web_search_service

app.include_router(chat_router, prefix="/api")
app.include_router(temples_router, prefix="/api")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "generation_enabled": llm_service.is_enabled,
        "llm_configured": bool(settings.llm_model),
        "collection": settings.collection_name,
        "chroma_persist_dir": settings.chroma_persist_dir,
        "indexed_chunks": retrieval_service.count(),
    }
