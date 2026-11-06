from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app import sqlite_compat


def test_sqlite_compat_accepts_minimum_supported_version(monkeypatch):
    monkeypatch.setattr(sqlite_compat.sqlite3, "sqlite_version_info", (3, 35, 0))
    monkeypatch.setattr(sqlite_compat.sqlite3, "sqlite_version", "3.35.0")
    assert sqlite_compat.ensure_supported_sqlite() == "3.35.0"


def test_sqlite_compat_rejects_older_version_clearly(monkeypatch):
    monkeypatch.setattr(sqlite_compat.sqlite3, "sqlite_version_info", (3, 34, 1))
    monkeypatch.setattr(sqlite_compat.sqlite3, "sqlite_version", "3.34.1")
    with pytest.raises(RuntimeError, match=r"3\.34\.1.*requires SQLite >= 3\.35\.0"):
        sqlite_compat.ensure_supported_sqlite()


def test_retrieval_service_checks_sqlite_before_importing_chromadb():
    source = Path(__file__).parents[1] / "app" / "services" / "retrieval_service.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    body = tree.body
    guard_call = next(
        index for index, node in enumerate(body)
        if isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Name)
        and node.value.func.id == "ensure_supported_sqlite"
    )
    chroma_import = next(
        index for index, node in enumerate(body)
        if isinstance(node, ast.Import) and any(alias.name == "chromadb" for alias in node.names)
    )
    assert guard_call < chroma_import


def test_main_checks_sqlite_before_importing_application_routes_or_services():
    source = Path(__file__).parents[1] / "app" / "main.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    body = tree.body
    guard_call = next(
        index for index, node in enumerate(body)
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "_sqlite_version" for target in node.targets)
    )
    service_import = next(
        index for index, node in enumerate(body)
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("app.")
        and node.module != "app.sqlite_compat"
    )
    assert guard_call < service_import
