"""Shared test fixtures.

Conventions (from CLAUDE.md — Validation & Testing):
- mock 최소화: 외부 API/네트워크만 mock. 실제 객체 우선
- 테스트 격리: 각 테스트는 독립적으로 실행. 공유 상태 금지
- 인메모리 DB: SQLite in-memory 또는 동등한 경량 스토어 사용
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture()
def db_conn() -> Generator[sqlite3.Connection, None, None]:
    """In-memory SQLite connection — isolated per test."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture()
def project_root() -> Path:
    """Absolute path to project root."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture()
def tmp_workspace(tmp_path: Path) -> Path:
    """Temporary workspace directory for file-producing tests."""
    ws = tmp_path / "workspace"
    ws.mkdir()
    return ws
