from __future__ import annotations

import zipfile
import hashlib
import json

import chromadb
import numpy as np
import pytest

from app.config import Settings
from scripts.chroma_snapshot import backup, restore
from app.bootstrap import stage_snapshot, verify_snapshot


def _make_onnx_store(path):
    client = chromadb.PersistentClient(
        path=str(path), settings=chromadb.Settings(anonymized_telemetry=False)
    )
    collection = client.create_collection(
        "temple_heritage",
        metadata={"hnsw:space": "cosine", "embedding_backend": "onnx"},
    )
    vectors = np.zeros((2, 384), dtype=np.float32)
    vectors[0, 0] = 1.0
    vectors[1, 1] = 1.0
    collection.add(
        ids=["chunk-a", "chunk-b"],
        documents=["evidence a", "evidence b"],
        metadatas=[
            {"document_id": "doc-a", "source_url": "https://example.org/a"},
            {"document_id": "doc-b", "source_url": "https://example.org/b"},
        ],
        embeddings=vectors.tolist(),
    )
    client.close()


def test_onnx_snapshot_backup_and_restore_verify_integrity(tmp_path):
    source = tmp_path / "source"
    archive = tmp_path / "private" / "store.zip"
    target = tmp_path / "restored"
    _make_onnx_store(source)

    backup_report = backup(
        source, archive, "temple_heritage", "onnx", "test-model"
    )
    assert backup_report["count"] == 2
    assert backup_report["dimension"] == 384
    assert len(backup_report["archive_sha256"]) == 64
    assert archive.with_suffix(".zip.manifest.json").is_file()

    restore_report = restore(
        archive,
        archive.with_suffix(".zip.manifest.json"),
        target,
        "temple_heritage",
        2,
        "onnx",
    )
    assert restore_report["archive_sha256_verified"] is True
    assert restore_report["count"] == 2
    assert restore_report["ids_sha256"] == backup_report["ids_sha256"]
    assert restore_report["collection_metadata"]["embedding_backend"] == "onnx"


def test_snapshot_restore_rejects_tampered_archive(tmp_path):
    source = tmp_path / "source"
    archive = tmp_path / "store.zip"
    _make_onnx_store(source)
    backup(source, archive, "temple_heritage", "onnx", "test-model")

    with zipfile.ZipFile(archive, "a") as bundle:
        bundle.writestr("tampered.txt", "unexpected content")

    with pytest.raises(ValueError, match="SHA-256"):
        restore(
            archive,
            archive.with_suffix(".zip.manifest.json"),
            tmp_path / "should-not-exist",
            "temple_heritage",
            2,
            "onnx",
        )


def test_production_startup_settings_validate_index_expectation():
    settings = Settings(
        expected_indexed_chunks=557,
        embedding_warmup_on_startup=True,
    )
    assert settings.expected_indexed_chunks == 557
    assert settings.embedding_warmup_on_startup is True


def _snapshot_fixture(tmp_path):
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    payload = b"read-only snapshot fixture"
    (snapshot / "chroma.sqlite3").write_bytes(payload)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({
        "collection": "temple_heritage",
        "embedding_backend": "onnx",
        "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "model_revision": "e8f8c211226b894fcb81acc59f3b34ba3efd5f42",
        "onnx_file": "model_quint8_avx2.onnx",
        "tokenizer": "sentencepiece",
        "chunk_count": 557,
        "dimension": 384,
        "files": {"chroma.sqlite3": hashlib.sha256(payload).hexdigest()},
    }), encoding="utf-8")
    return snapshot, manifest


def test_bootstrap_verifies_snapshot_and_stages_separate_runtime_copy(tmp_path, monkeypatch):
    snapshot, manifest = _snapshot_fixture(tmp_path)
    (snapshot / "nested").mkdir()
    (snapshot / "nested" / "length.bin").write_bytes(b"index lengths")
    payload_hashes = {
        path.relative_to(snapshot).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in snapshot.rglob("*") if path.is_file()
    }
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    manifest_data["files"] = payload_hashes
    manifest.write_text(json.dumps(manifest_data), encoding="utf-8")
    for path in snapshot.rglob("*"):
        if path.is_dir():
            path.chmod(0o555)
        else:
            path.chmod(0o444)
    snapshot.chmod(0o555)
    runtime = tmp_path / "runtime" / "chroma"
    details = stage_snapshot(snapshot, manifest, runtime)
    assert details["chunk_count"] == 557
    assert (runtime / "chroma.sqlite3").read_bytes() == (snapshot / "chroma.sqlite3").read_bytes()
    assert snapshot != runtime
    assert hashlib.sha256((runtime / "nested" / "length.bin").read_bytes()).hexdigest() == payload_hashes["nested/length.bin"]
    for path in [runtime, *runtime.rglob("*")]:
        if path.is_dir():
            assert path.stat().st_mode & 0o200
        else:
            assert path.stat().st_mode & 0o200
    assert {
        path.relative_to(snapshot).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in snapshot.rglob("*") if path.is_file()
    } == payload_hashes
    for path in snapshot.rglob("*"):
        path.chmod(0o755 if path.is_dir() else 0o644)
    snapshot.chmod(0o755)


def test_bootstrap_rejects_runtime_path_overlapping_snapshot(tmp_path):
    snapshot, manifest = _snapshot_fixture(tmp_path)
    with pytest.raises(RuntimeError, match="overlaps immutable snapshot"):
        stage_snapshot(snapshot, manifest, snapshot / "runtime")


def test_bootstrap_fails_clearly_for_missing_or_corrupt_snapshot(tmp_path):
    snapshot, manifest = _snapshot_fixture(tmp_path)
    with pytest.raises(RuntimeError, match="Bundled Chroma snapshot validation failed"):
        verify_snapshot(tmp_path / "missing", manifest)
    (snapshot / "chroma.sqlite3").write_bytes(b"corrupt")
    with pytest.raises(RuntimeError, match="checksum mismatch"):
        verify_snapshot(snapshot, manifest)
