FROM python:3.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HOME=/tmp/huggingface \
    CHROMA_PERSIST_DIR=/tmp/temple-chroma-runtime \
    CHROMA_SNAPSHOT_DIR=/app/data/chroma_snapshot \
    CHROMA_SNAPSHOT_MANIFEST=/app/data/chroma_onnx_snapshot_manifest.json \
    COLLECTION_NAME=temple_heritage \
    EMBEDDING_BACKEND=onnx \
    EMBEDDING_INDEX_BACKEND=onnx \
    EMBEDDING_ONNX_TOKENIZER=sentencepiece \
    EMBEDDING_ONNX_FILE=model_quint8_avx2.onnx \
    EMBEDDING_MAX_SEQ_LENGTH=128 \
    EMBEDDING_NUM_THREADS=1 \
    EMBEDDING_BATCH_SIZE=16 \
    EMBEDDING_REVISION=e8f8c211226b894fcb81acc59f3b34ba3efd5f42 \
    EMBEDDING_WARMUP_ON_STARTUP=true \
    EXPECTED_INDEXED_CHUNKS=557 \
    WEB_SEARCH_ENABLED=false

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /app app

COPY requirements-onnx.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "import sqlite3; print('Build SQLite runtime:', sqlite3.sqlite_version); assert sqlite3.sqlite_version_info >= (3, 35, 0), 'ChromaDB requires SQLite >= 3.35.0'"

COPY app ./app
COPY data/catalogue.json ./data/catalogue.json
COPY data/raw/temple_sources.json ./data/raw/temple_sources.json
COPY data/chroma_onnx ./data/chroma_snapshot
COPY data/chroma_onnx_snapshot_manifest.json ./data/chroma_onnx_snapshot_manifest.json

# The bundled database and checksum manifest are immutable to the service user.
# bootstrap verifies the snapshot and stages a writable copy under /tmp because
# Chroma requires a writable SQLite directory at runtime.
RUN chmod -R a-w /app/data && chmod -R a+rX /app/data \
    && chown -R root:root /app
USER app

EXPOSE 10000
CMD ["python", "-m", "app.bootstrap"]
