from __future__ import annotations

import os
import tempfile

import pytest

from app.migrations import get_migrations, run_migrations


@pytest.mark.asyncio
async def test_run_migrations_creates_version_table() -> None:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        await run_migrations(db_path)
        import aiosqlite

        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute("SELECT MAX(version) FROM schema_version")
            row = await cursor.fetchone()
            migrations = get_migrations()
            expected = max(migrations.keys())
            assert row is not None and row[0] == expected
    finally:
        os.unlink(db_path)


@pytest.mark.asyncio
async def test_run_migrations_is_idempotent() -> None:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        await run_migrations(db_path)
        await run_migrations(db_path)
        import aiosqlite

        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM schema_version")
            row = await cursor.fetchone()
            migrations = get_migrations()
            expected = len(migrations)
            assert row is not None and row[0] == expected
    finally:
        os.unlink(db_path)


def test_get_migrations_returns_dict() -> None:
    migrations = get_migrations()
    assert isinstance(migrations, dict)
    assert 1 in migrations
