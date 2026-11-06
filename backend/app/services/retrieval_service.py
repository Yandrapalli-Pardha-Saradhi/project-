from __future__ import annotations

from typing import List, Optional

from app.sqlite_compat import ensure_supported_sqlite

ensure_supported_sqlite()

import chromadb

from app.services.embedding_service import EmbeddingService

# Local-first: disable ChromaDB's anonymized telemetry.
_CHROMA_SETTINGS = chromadb.Settings(anonymized_telemetry=False)


class RetrievedChunk:
    """A text chunk returned by vector search, with its distance and metadata."""

    def __init__(self, chunk_id: str, text: str, distance: float, metadata: dict):
        self.chunk_id = chunk_id
        self.text = text
        self.distance = float(distance)
        self.metadata = dict(metadata or {})


class RetrievalService:
    """Vector search over a persistent ChromaDB collection."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        persist_dir: str,
        collection_name: str,
    ):
        self.embedding_service = embedding_service
        self.client = chromadb.PersistentClient(path=persist_dir, settings=_CHROMA_SETTINGS)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={
                "hnsw:space": "cosine",
                "embedding_backend": getattr(embedding_service, "backend", "pytorch"),
            },
        )
        indexed_backend = (self.collection.metadata or {}).get("embedding_backend", "pytorch")
        query_backend = getattr(embedding_service, "backend", "pytorch")
        if indexed_backend != query_backend:
            raise ValueError(
                f"Collection {collection_name!r} is indexed with {indexed_backend!r}, "
                f"but queries are configured for {query_backend!r}. Use a separate "
                "collection and re-index before changing embedding backends."
            )

    def count(self) -> int:
        try:
            return self.collection.count()
        except Exception:
            return 0

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        temple_id: Optional[str] = None,
        state: Optional[str] = None,
        district: Optional[str] = None,
    ) -> List[RetrievedChunk]:
        if not query or not query.strip():
            return []
        total = self.count()
        if total == 0:
            return []
        n_results = min(top_k, total)
        filters = [
            {key: value} for key, value in (
                ("temple_id", temple_id), ("state", state), ("district", district)
            ) if value
        ]
        where = filters[0] if len(filters) == 1 else {"$and": filters} if filters else None
        query_embedding = self.embedding_service.embed_query(query.strip())
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        chunks: List[RetrievedChunk] = []
        ids = results.get("ids") or [[]]
        documents = results.get("documents") or [[]]
        metadatas = results.get("metadatas") or [[]]
        distances = results.get("distances") or [[]]
        for chunk_id, text, metadata, distance in zip(
            ids[0], documents[0], metadatas[0], distances[0]
        ):
            chunks.append(
                RetrievedChunk(chunk_id=chunk_id, text=text, distance=distance, metadata=metadata)
            )
        return chunks
