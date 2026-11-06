from __future__ import annotations

from pathlib import Path
from typing import List, Literal, Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "temple_sources.json"
DEFAULT_CHROMA_PERSIST_DIR = DATA_DIR / "chroma"
DEFAULT_COLLECTION_NAME = "temple_heritage"

# Supported answer languages: English, Telugu, Tamil, Hindi.
SUPPORTED_LANGUAGES = ("en", "te", "ta", "hi")
LANGUAGE_NAMES = {
    "en": "English",
    "te": "Telugu",
    "ta": "Tamil",
    "hi": "Hindi",
}


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and .env."""

    app_name: str = Field(default="Temple & Heritage Information Assistant")
    debug: bool = Field(default=False)

    # LLM provider: OpenAI-compatible chat completions (includes OpenRouter).
    llm_base_url: str = Field(default="https://openrouter.ai/api/v1")
    llm_api_key: Optional[SecretStr] = Field(default=None)
    llm_model: Optional[str] = Field(default=None)

    # Embedding model (multilingual).
    embedding_model: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    # Keep PyTorch as the compatibility default. An ONNX runtime must only be
    # paired with a collection indexed by the same backend.
    embedding_backend: Literal["pytorch", "onnx"] = Field(default="pytorch")
    embedding_index_backend: Literal["pytorch", "onnx"] = Field(default="pytorch")
    embedding_onnx_file: str = Field(default="model_quint8_avx2.onnx")
    embedding_onnx_tokenizer: Literal["sentencepiece", "tokenizers"] = Field(default="sentencepiece")
    embedding_onnx_graph_optimization_level: Literal["disable", "basic", "extended", "all"] = Field(default="all")
    embedding_max_seq_length: int = Field(default=128, ge=1, le=512)
    embedding_num_threads: int = Field(default=1, ge=1, le=16)
    embedding_batch_size: int = Field(default=16, ge=1, le=256)
    embedding_revision: Optional[str] = Field(default=None)
    embedding_warmup_on_startup: bool = Field(default=False)

    # Persistent local vector store.
    chroma_persist_dir: str = Field(default=str(DEFAULT_CHROMA_PERSIST_DIR))
    collection_name: str = Field(default=DEFAULT_COLLECTION_NAME)
    expected_indexed_chunks: Optional[int] = Field(default=None, ge=1)

    # Document chunking.
    chunk_size: int = Field(default=500)
    chunk_overlap: int = Field(default=50)

    # Conservative public-source collection controls. Per-source robots and
    # allowlist checks remain mandatory regardless of these values.
    collector_timeout_seconds: float = Field(default=12.0, gt=0, le=60)
    collector_retries: int = Field(default=2, ge=0, le=5)
    collector_backoff_seconds: float = Field(default=0.5, ge=0, le=30)
    collector_min_domain_interval: float = Field(default=1.0, ge=0, le=60)

    # Retrieval.
    top_k: int = Field(default=5)
    relevance_threshold: float = Field(default=0.7)

    # CORS origins (comma-separated). Do not use "*" in production.
    cors_origins: str = Field(default="")

    # Optional web-search extension for discovering sources not in the KB.
    web_search_enabled: bool = Field(default=False)
    web_search_timeout: float = Field(default=10.0)

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.cors_origins:
            return []
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def generation_enabled(self) -> bool:
        """Generation is available only when both an API key and a model are configured."""
        if not self.llm_api_key:
            return False
        key = self.llm_api_key.get_secret_value()
        return bool(key and self.llm_model)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }
