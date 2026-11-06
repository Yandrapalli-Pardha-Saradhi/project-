"""SQLite runtime check required before importing ChromaDB."""
from __future__ import annotations

import sqlite3

MINIMUM_SQLITE_VERSION = (3, 35, 0)


def ensure_supported_sqlite() -> str:
    """Return the linked SQLite version, or fail before ChromaDB is imported."""
    version = sqlite3.sqlite_version_info
    actual = sqlite3.sqlite_version
    if tuple(version[:3]) < MINIMUM_SQLITE_VERSION:
        raise RuntimeError(
            "Unsupported SQLite runtime: Python sqlite3 is linked to "
            f"SQLite {actual}; ChromaDB requires SQLite >= 3.35.0. "
            "Use the Bookworm production image or a newer SQLite runtime."
        )
    return actual
