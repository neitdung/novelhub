from __future__ import annotations

import os
import tempfile
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.migrations import run_migrations


@pytest.fixture(autouse=True)
async def setup_db() -> AsyncGenerator[None, None]:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    old_db_path = os.environ.get("NOVELHUB_DB_PATH")
    os.environ["NOVELHUB_DB_PATH"] = db_path
    try:
        await run_migrations(db_path)
        yield
    finally:
        if old_db_path is not None:
            os.environ["NOVELHUB_DB_PATH"] = old_db_path
        else:
            os.environ.pop("NOVELHUB_DB_PATH", None)
        Path(db_path).unlink(missing_ok=True)


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
