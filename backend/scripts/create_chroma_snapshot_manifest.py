"""Create integrity metadata for the read-only ONNX snapshot."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import chromadb

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data" / "chroma_onnx"
TARGET = ROOT / "data" / "chroma_onnx_snapshot_manifest.json"


def main() -> None:
    client = chromadb.PersistentClient(path=str(SNAPSHOT), settings=chromadb.Settings(anonymized_telemetry=False))
    collection = client.get_collection("temple_heritage")
    rows = collection.get(include=["documents", "metadatas", "embeddings"])
    ids = sorted(rows["ids"])
    metadata = collection.metadata or {}
    if metadata.get("embedding_backend") != "onnx":
        raise SystemExit("Refusing to manifest a collection without embedding_backend=onnx")
    dimensions = {len(vector) for vector in rows["embeddings"]}
    if len(ids) != 557 or len(set(ids)) != 557 or dimensions != {384}:
        raise SystemExit(f"Unexpected snapshot shape: count={len(ids)} dimensions={dimensions}")
    # Closing before file hashing captures SQLite's final checkpointed bytes.
    client.close()
    files = {
        path.relative_to(SNAPSHOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(SNAPSHOT.rglob("*")) if path.is_file()
    }
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "collection": "temple_heritage",
        "embedding_backend": "onnx",
        "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "model_revision": "e8f8c211226b894fcb81acc59f3b34ba3efd5f42",
        "onnx_file": "model_quint8_avx2.onnx",
        "tokenizer": "sentencepiece",
        "chunk_count": len(ids),
        "dimension": 384,
        "chunk_id_sha256": hashlib.sha256("\n".join(ids).encode()).hexdigest(),
        "files": files,
    }
    TARGET.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
