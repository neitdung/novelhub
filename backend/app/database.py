from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aiosqlite


def get_db_path() -> str:
    return os.environ.get("NOVELHUB_DB_PATH", "novelhub.db")


async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    db_path = get_db_path()
    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        yield db


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[aiosqlite.Connection, None]:
    db_path = get_db_path()
    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        yield db


async def check_db_health() -> dict[str, str]:
    try:
        db_path = get_db_path()
        async with aiosqlite.connect(db_path) as db:
            await db.execute("SELECT 1")
            return {"database": "ok"}
    except Exception:
        return {"database": "error"}
