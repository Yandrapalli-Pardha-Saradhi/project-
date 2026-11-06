from __future__ import annotations

import logging
from pathlib import Path

from app.sqlite_compat import ensure_supported_sqlite

_sqlite_version = ensure_supported_sqlite()
logging.getLogger("temple_heritage.startup").info(
    "SQLite runtime: %s (ChromaDB minimum: 3.35.0)", _sqlite_version
)

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

logger = logging.getLogger("temple_heritage.memory")
settings = Settings()
if settings.embedding_warmup_on_startup and not logger.handlers:
    # Keep the optional deployment probe visible in Docker logs even when the
    # Uvicorn root logger does not route application INFO records.
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def _memory_snapshot() -> dict[str, object]:
    """Read Linux RSS/cgroup counters without adding a runtime dependency."""
    values: dict[str, int] = {}
    try:
        for line in Path("/proc/self/status").read_text(encoding="utf-8").splitlines():
            if line.startswith("VmRSS:"):
                values["process_rss_kb"] = int(line.split()[1])
                break
    except (OSError, ValueError, IndexError):
        pass
    for key in ("memory.current", "memory.peak"):
        try:
            values[key.replace(".", "_") + "_bytes"] = int(
                Path("/sys/fs/cgroup", key).read_text(encoding="ascii").strip()
            )
        except (OSError, ValueError):
            pass
    try:
        event_values = {}
        for line in Path("/sys/fs/cgroup/memory.events").read_text(encoding="ascii").splitlines():
            name, value = line.split()
            event_values[name] = int(value)
        values["memory_events"] = event_values
    except (OSError, ValueError):
        pass
    return values


def _log_memory_stage(stage: str, **details: object) -> None:
    logger.info("MEMORY_STAGE %s counters=%s details=%s", stage, _memory_snapshot(), details)

app = FastAPI(title=settings.app_name, debug=settings.debug)
_log_memory_stage("fastapi_initialized")

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

embedding_service = EmbeddingService.from_settings(settings)
try:
    retrieval_service = RetrievalService(
        embedding_service, settings.chroma_persist_dir, settings.collection_name
    )
except Exception as exc:
    raise RuntimeError(
        f"Could not open Chroma collection {settings.collection_name!r} at "
        f"{settings.chroma_persist_dir!r}; verify the bundled/restored snapshot and "
        "its ONNX backend metadata."
    ) from exc
if (
    settings.expected_indexed_chunks is not None
    and retrieval_service.count() != settings.expected_indexed_chunks
):
    raise RuntimeError(
        f"Configured Chroma collection {settings.collection_name!r} contains "
        f"{retrieval_service.count()} chunks; expected "
        f"{settings.expected_indexed_chunks}. Refusing to serve an incomplete index."
    )
_log_memory_stage(
    "chromadb_initialized",
    collection=settings.collection_name,
    chunks=retrieval_service.count(),
    embedding_backend=settings.embedding_backend,
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

if settings.embedding_warmup_on_startup:
    # Production images opt in so model download/loading failures occur before
    # the service passes its health check or accepts user traffic.
    _ = embedding_service.model
    _log_memory_stage("embedding_model_warmed", backend=settings.embedding_backend)


@app.middleware("http")
async def log_chat_memory(request, call_next):
    response = await call_next(request)
    if request.url.path == "/api/chat":
        _log_memory_stage("chat_request_complete", status=response.status_code)
    return response

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
