"""Create and restore integrity-checked Chroma directory snapshots.

Stop the API and all writers before creating a backup. The archive and its
manifest are a pair; store them in a private location. Restore always targets
a new path and verifies checksum, collection, backend, count, IDs and vectors
before atomically publishing the directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

import chromadb
import numpy as np


def client(path: Path):
    return chromadb.PersistentClient(
        path=str(path), settings=chromadb.Settings(anonymized_telemetry=False)
    )


def close_client(value: Any) -> None:
    close = getattr(value, "close", None)
    if callable(close):
        close()
        return
    stop = getattr(getattr(value, "_system", None), "stop", None)
    if callable(stop):
        stop()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ids_digest(ids: list[str]) -> str:
    return hashlib.sha256("\n".join(sorted(ids)).encode("utf-8")).hexdigest()


def inspect_store(path: Path, collection_name: str, expected_backend: str) -> dict[str, Any]:
    db = client(path)
    try:
        collection = db.get_collection(collection_name)
        metadata = collection.metadata or {}
        backend = metadata.get("embedding_backend", "pytorch")
        if backend != expected_backend:
            raise ValueError(f"Collection backend is {backend!r}, expected {expected_backend!r}")
        count = collection.count()
        result = collection.get(limit=count, include=["embeddings"])
        ids = result["ids"]
        vectors = np.asarray(result["embeddings"], dtype=np.float32)
        if len(ids) != count or vectors.ndim != 2 or vectors.shape[0] != count:
            raise ValueError("Collection count, IDs and embeddings are inconsistent")
        if len(set(ids)) != count:
            raise ValueError("Duplicate IDs in collection")
        if not np.isfinite(vectors).all():
            raise ValueError("Collection contains a non-finite vector")
        norms = np.linalg.norm(vectors, axis=1)
        return {
            "collection": collection_name,
            "collection_metadata": metadata,
            "count": count,
            "dimension": int(vectors.shape[1]),
            "ids_sha256": ids_digest(ids),
            "normalized": bool(np.allclose(norms, 1.0, atol=1e-4)),
            "norm_min": float(norms.min()) if count else None,
            "norm_max": float(norms.max()) if count else None,
        }
    finally:
        close_client(db)


def backup(source: Path, archive: Path, collection: str, backend: str, model: str,
           model_revision: str | None = None, embedding_artifact: str | None = None,
           tokenizer: str | None = None, max_seq_length: int | None = None) -> dict[str, Any]:
    source, archive = source.resolve(), archive.resolve()
    manifest_path = archive.with_suffix(archive.suffix + ".manifest.json")
    if not source.is_dir():
        raise FileNotFoundError(f"Source store not found: {source}")
    if archive.exists() or manifest_path.exists():
        raise FileExistsError("Archive or manifest already exists; backups are never overwritten")
    store_info = inspect_store(source, collection, backend)
    if not store_info["normalized"]:
        raise ValueError("Refusing to back up an index with non-normalized vectors")
    archive.parent.mkdir(parents=True, exist_ok=True)
    staging_archive = archive.with_name(f"{archive.name}.partial-{uuid.uuid4().hex}")
    try:
        with zipfile.ZipFile(staging_archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as output:
            for path in sorted(source.rglob("*")):
                if path.is_file():
                    output.write(path, path.relative_to(source).as_posix())
        checksum = sha256_file(staging_archive)
        manifest = {
            "schema_version": 1,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "archive_file": archive.name,
            "archive_sha256": checksum,
            "embedding_backend": backend,
            "embedding_model": model,
            "model_revision": model_revision,
            "embedding_artifact": embedding_artifact,
            "tokenizer": tokenizer,
            "max_seq_length": max_seq_length,
            "dimension": store_info["dimension"],
            **store_info,
        }
        staging_archive.rename(archive)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {"archive": str(archive), "manifest": str(manifest_path), **manifest}
    except Exception:
        if staging_archive.exists():
            staging_archive.unlink()
        raise


def safe_extract(archive: Path, destination: Path) -> None:
    root = destination.resolve()
    with zipfile.ZipFile(archive, "r") as bundle:
        for member in bundle.infolist():
            item = PurePosixPath(member.filename)
            if item.is_absolute() or ".." in item.parts or not item.parts:
                raise ValueError(f"Unsafe path in archive: {member.filename!r}")
            mode = member.external_attr >> 16
            if mode and (mode & 0o170000) == 0o120000:
                raise ValueError(f"Refusing symlink in archive: {member.filename!r}")
            target = (destination / Path(*item.parts)).resolve()
            if not target.is_relative_to(root):
                raise ValueError(f"Unsafe extracted path: {member.filename!r}")
        bundle.extractall(destination)


def restore(archive: Path, manifest_path: Path, target: Path, collection: str,
            expected_count: int, expected_backend: str) -> dict[str, Any]:
    archive, manifest_path, target = archive.resolve(), manifest_path.resolve(), target.resolve()
    if target.exists():
        raise FileExistsError(f"Restore target already exists: {target}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("archive_sha256") != sha256_file(archive):
        raise ValueError("Archive SHA-256 does not match its manifest")
    if manifest.get("collection") != collection:
        raise ValueError("Collection name does not match the manifest")
    if manifest.get("count") != expected_count:
        raise ValueError(f"Manifest count {manifest.get('count')} does not match expected {expected_count}")
    if manifest.get("embedding_backend") != expected_backend:
        raise ValueError("Embedding backend does not match the manifest")
    if manifest.get("dimension") != 384:
        raise ValueError(f"Unexpected embedding dimension in manifest: {manifest.get('dimension')}")

    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.with_name(f"{target.name}.restore-{uuid.uuid4().hex}")
    publish_staging = target.with_name(f"{target.name}.publish-{uuid.uuid4().hex}")
    staging.mkdir()
    try:
        safe_extract(archive, staging)
        inspected = inspect_store(staging, collection, expected_backend)
        if inspected["count"] != expected_count:
            raise ValueError(f"Restored collection count is {inspected['count']}, expected {expected_count}")
        if inspected["dimension"] != manifest["dimension"]:
            raise ValueError("Restored vector dimensions differ from the manifest")
        if inspected["ids_sha256"] != manifest["ids_sha256"]:
            raise ValueError("Restored IDs differ from the manifest")
        if not inspected["normalized"]:
            raise ValueError("Restored vectors are not normalized")
        if inspected["collection_metadata"] != manifest["collection_metadata"]:
            raise ValueError("Restored collection metadata differs from the manifest")
        # Windows may keep SQLite handles associated with the directory just
        # validated. Publish a fresh byte-for-byte copy so the atomic rename
        # never targets a directory that has been opened by Chroma.
        shutil.copytree(staging, publish_staging)
        publish_info = inspect_store(publish_staging, collection, expected_backend)
        if publish_info != inspected:
            raise ValueError("Prepared restore copy differs from the validated archive extraction")
        publish_staging.rename(target)
        final_info = inspect_store(target, collection, expected_backend)
        if final_info != inspected:
            raise ValueError("Final published restore differs from the verified staging directory")
        return {"restored_path": str(target), "archive_sha256_verified": True, **final_info}
    except Exception:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        if publish_staging.exists():
            shutil.rmtree(publish_staging, ignore_errors=True)
        raise
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    backup_parser = sub.add_parser("backup")
    backup_parser.add_argument("--source", type=Path, required=True)
    backup_parser.add_argument("--archive", type=Path, required=True)
    backup_parser.add_argument("--collection", default="temple_heritage")
    backup_parser.add_argument("--backend", choices=["pytorch", "onnx"], required=True)
    backup_parser.add_argument("--model", default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    backup_parser.add_argument("--model-revision")
    backup_parser.add_argument("--embedding-artifact")
    backup_parser.add_argument("--tokenizer")
    backup_parser.add_argument("--max-seq-length", type=int)
    restore_parser = sub.add_parser("restore")
    restore_parser.add_argument("--archive", type=Path, required=True)
    restore_parser.add_argument("--manifest", type=Path, required=True)
    restore_parser.add_argument("--target", type=Path, required=True)
    restore_parser.add_argument("--collection", default="temple_heritage")
    restore_parser.add_argument("--expected-count", type=int, required=True)
    restore_parser.add_argument("--backend", choices=["pytorch", "onnx"], required=True)
    args = parser.parse_args()
    try:
        if args.command == "backup":
            report = backup(
                args.source, args.archive, args.collection, args.backend, args.model,
                args.model_revision, args.embedding_artifact, args.tokenizer, args.max_seq_length,
            )
        else:
            report = restore(args.archive, args.manifest, args.target, args.collection,
                             args.expected_count, args.backend)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    except (FileExistsError, FileNotFoundError, OSError, ValueError, zipfile.BadZipFile) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
