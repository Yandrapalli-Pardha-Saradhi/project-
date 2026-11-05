"""Copy an offline PersistentClient store and verify IDs, metadata and vectors.

Example (run from backend):
python scripts/migrate_chroma_store.py --source data/chroma --target /var/data/chroma-imported
"""
from __future__ import annotations

import argparse
import json
import shutil
import uuid
from pathlib import Path
from typing import Any

import chromadb


def _client(path: Path):
    return chromadb.PersistentClient(
        path=str(path), settings=chromadb.Settings(anonymized_telemetry=False)
    )


def _close_client(client: Any) -> None:
    """Release Chroma's SQLite handles before a directory rename (notably Windows)."""
    close = getattr(client, "close", None)
    if callable(close):
        close()
        return
    system = getattr(client, "_system", None)
    stop = getattr(system, "stop", None)
    if callable(stop):
        stop()


def _snapshot(path: Path, collection_name: str) -> dict[str, Any]:
    client = _client(path)
    try:
        collection = client.get_collection(name=collection_name)
        count = collection.count()
        result = collection.get(
            limit=count,
            include=["documents", "metadatas", "embeddings"],
        )
        if len(result["ids"]) != count or any(
            len(result[key]) != count for key in ("documents", "metadatas", "embeddings")
        ):
            raise RuntimeError(f"Could not read a complete snapshot from {path}")
        entries = {
            chunk_id: (document, metadata, embedding)
            for chunk_id, document, metadata, embedding in zip(
                result["ids"], result["documents"], result["metadatas"], result["embeddings"]
            )
        }
        if len(entries) != count:
            raise RuntimeError("Duplicate chunk IDs found in source collection")
        return {"count": count, "entries": entries}
    finally:
        _close_client(client)


def _same_data(left: dict[str, Any], right: dict[str, Any]) -> bool:
    if left["count"] != right["count"] or left["entries"].keys() != right["entries"].keys():
        return False
    import numpy as np

    for chunk_id, (left_doc, left_meta, left_embedding) in left["entries"].items():
        right_doc, right_meta, right_embedding = right["entries"][chunk_id]
        if left_doc != right_doc or left_meta != right_meta:
            return False
        if not np.array_equal(left_embedding, right_embedding):
            return False
    return True


def migrate(source: Path, target: Path, collection_name: str, expected_count: int, dry_run: bool) -> dict[str, Any]:
    source = source.resolve()
    target = target.resolve()
    if source == target or source in target.parents or target in source.parents:
        raise ValueError("Source and target must be separate, non-nested directories")
    if not source.is_dir():
        raise FileNotFoundError(f"Chroma source directory not found: {source}")

    source_snapshot = _snapshot(source, collection_name)
    if source_snapshot["count"] != expected_count:
        raise ValueError(
            f"Expected {expected_count} chunks, found {source_snapshot['count']}; "
            "verify the source database and pass the correct --expected-count if it changed"
        )
    if target.exists():
        raise FileExistsError(
            f"Target already exists: {target}. Choose a new empty path; migration never overwrites a target."
        )
    if dry_run:
        return {
            "dry_run": True,
            "source": str(source),
            "target": str(target),
            "collection": collection_name,
            "chunks": source_snapshot["count"],
            "ids_metadata_and_embeddings_validated": True,
        }

    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.with_name(f"{target.name}.staging-{uuid.uuid4().hex}")
    try:
        shutil.copytree(source, staging, copy_function=shutil.copy2)
        copied_snapshot = _snapshot(staging, collection_name)
        if not _same_data(source_snapshot, copied_snapshot):
            raise RuntimeError("Copied Chroma data differs from source; target was not published")
        # Atomic rename on the same mounted filesystem; destination must remain absent.
        staging.rename(target)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise

    final_snapshot = _snapshot(target, collection_name)
    if not _same_data(source_snapshot, final_snapshot):
        raise RuntimeError("Final Chroma verification failed after publishing the copied directory")
    return {
        "dry_run": False,
        "source": str(source),
        "target": str(target),
        "collection": collection_name,
        "chunks": final_snapshot["count"],
        "ids_metadata_and_embeddings_validated": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--collection", default="temple_heritage")
    parser.add_argument("--expected-count", type=int, default=296)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(migrate(args.source, args.target, args.collection, args.expected_count, args.dry_run), indent=2))
    except (FileExistsError, FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
