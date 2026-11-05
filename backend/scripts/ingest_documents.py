#!/usr/bin/env python3
"""Backward-compatible entry point for the ingestion CLI.

From ``backend/`` run ``python scripts/ingest_documents.py`` to index, or pass
one of the ``collect``, ``validate``, ``index``, ``run`` or ``report`` commands.
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.ingestion import main as ingestion_main  # noqa: E402


def main() -> None:
    arguments = sys.argv[1:]
    if not arguments or arguments[0].startswith("-"):
        arguments = ["index", *arguments]
    raise SystemExit(ingestion_main(arguments))


if __name__ == "__main__":
    main()
