"""Validate the immutable bundled Chroma snapshot and stage it for runtime use."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import sys
from pathlib import Path

from app.sqlite_compat import ensure_supported_sqlite


def _reject_overlapping_paths(snapshot_dir: Path, runtime_dir: Path) -> None:
    snapshot = snapshot_dir.resolve()
    runtime = runtime_dir.resolve()
    if snapshot == runtime or snapshot in runtime.parents or runtime in snapshot.parents:
        raise RuntimeError(
            f"Unsafe Chroma paths: runtime directory {runtime} overlaps immutable "
            f"snapshot directory {snapshot}"
        )
    if runtime_dir.is_symlink():
        raise RuntimeError(f"Unsafe Chroma runtime path must not be a symlink: {runtime_dir}")


def _make_runtime_tree_writable(runtime_dir: Path) -> None:
    """Add owner write access to every staged directory and file."""
    for current, directories, files in os.walk(runtime_dir):
        current_path = Path(current)
        current_path.chmod(stat.S_IMODE(current_path.stat().st_mode) | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        for filename in files:
            file_path = current_path / filename
            file_path.chmod(stat.S_IMODE(file_path.stat().st_mode) | stat.S_IRUSR | stat.S_IWUSR)
        # Ensure traversal is possible even when the bundled directory mode was read-only.
        for dirname in directories:
            directory = current_path / dirname
            directory.chmod(stat.S_IMODE(directory.stat().st_mode) | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)


def verify_snapshot(snapshot_dir: Path, manifest_path: Path) -> dict:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        files = manifest["files"]
        if not isinstance(files, dict) or not files:
            raise ValueError("manifest has no file checksums")
        expected_identity = {
            "collection": "temple_heritage",
            "embedding_backend": "onnx",
            "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            "model_revision": "e8f8c211226b894fcb81acc59f3b34ba3efd5f42",
            "onnx_file": "model_quint8_avx2.onnx",
            "tokenizer": "sentencepiece",
        }
        for key, expected in expected_identity.items():
            if manifest.get(key) != expected:
                raise ValueError(f"manifest {key} is not the expected ONNX deployment value")
        for relative, expected in files.items():
            path = (snapshot_dir / relative).resolve()
            if snapshot_dir.resolve() not in path.parents:
                raise ValueError(f"invalid snapshot file path: {relative}")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != expected:
                raise ValueError(f"checksum mismatch for {relative}")
        if int(manifest.get("chunk_count", 0)) != 557:
            raise ValueError("snapshot manifest chunk count is not 557")
        if int(manifest.get("dimension", 0)) != 384:
            raise ValueError("snapshot embedding dimension is not 384")
        return manifest
    except Exception as exc:
        raise RuntimeError(f"Bundled Chroma snapshot validation failed: {exc}") from exc


def stage_snapshot(snapshot_dir: Path, manifest_path: Path, runtime_dir: Path) -> dict:
    _reject_overlapping_paths(snapshot_dir, runtime_dir)
    manifest = verify_snapshot(snapshot_dir, manifest_path)
    if runtime_dir.exists():
        if runtime_dir.is_dir():
            for current, directories, files in os.walk(runtime_dir):
                path = Path(current)
                path.chmod(stat.S_IMODE(path.stat().st_mode) | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                for name in files:
                    file_path = path / name
                    file_path.chmod(stat.S_IMODE(file_path.stat().st_mode) | stat.S_IWUSR)
        shutil.rmtree(runtime_dir)
    runtime_dir.parent.mkdir(parents=True, exist_ok=True)
    # copyfile creates fresh writable files; copy2/copytree defaults would carry
    # the immutable bundle's read-only file modes into the runtime database.
    shutil.copytree(snapshot_dir, runtime_dir, copy_function=shutil.copyfile)
    _make_runtime_tree_writable(runtime_dir)
    verify_snapshot(runtime_dir, manifest_path)
    verify_snapshot(snapshot_dir, manifest_path)
    return manifest


def main() -> None:
    sqlite_version = ensure_supported_sqlite()
    print(f"SQLite runtime: {sqlite_version} (ChromaDB minimum: 3.35.0)", flush=True)
    snapshot = Path(os.getenv("CHROMA_SNAPSHOT_DIR", "/app/data/chroma_snapshot"))
    manifest = Path(os.getenv("CHROMA_SNAPSHOT_MANIFEST", "/app/data/chroma_onnx_snapshot_manifest.json"))
    runtime = Path(os.getenv("CHROMA_PERSIST_DIR", "/tmp/temple-chroma-runtime"))
    try:
        details = stage_snapshot(snapshot, manifest, runtime)
    except Exception as exc:
        print(str(exc), file=sys.stderr, flush=True)
        raise SystemExit(1) from exc
    os.environ["CHROMA_PERSIST_DIR"] = str(runtime)
    print(
        f"Validated immutable ONNX Chroma snapshot: chunks={details['chunk_count']} "
        f"dimension={details['dimension']}; runtime_copy={runtime}",
        flush=True,
    )
    port = os.getenv("PORT", "10000")
    os.execvp("uvicorn", ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", port, "--workers", "1"])


if __name__ == "__main__":
    main()
