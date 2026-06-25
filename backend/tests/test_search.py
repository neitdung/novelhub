from __future__ import annotations

import pytest

from app.database import get_db_context
from app.kb.crud import create_entity
from app.kb.schemas import EntityCreate
from app.search import rebuild_fts, search_entities, setup_fts


async def _create_novel(novel_id: int = 1) -> None:
    async with get_db_context() as db:
        await db.execute(
            "INSERT INTO novels (id, title, author, file_path, file_hash)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                novel_id,
                f"Test Novel {novel_id}",
                "Author",
                f"/tmp/{novel_id}.txt",
                f"hash{novel_id}",
            ),
        )
        await db.commit()


@pytest.mark.asyncio
async def test_setup_fts() -> None:
    await setup_fts()
    async with get_db_context() as db:
        cursor = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='entities_fts'"
        )
        assert await cursor.fetchone() is not None


@pytest.mark.asyncio
async def test_search_entities() -> None:
    await _create_novel(1)
    await setup_fts()

    await create_entity(
        EntityCreate(novel_id=1, name="Alice", entity_type="character")
    )
    await create_entity(
        EntityCreate(novel_id=1, name="Bob", entity_type="character")
    )

    await rebuild_fts()

    results = await search_entities("Alice")
    assert len(results) == 1
    assert results[0]["name"] == "Alice"


@pytest.mark.asyncio
async def test_search_entities_by_novel() -> None:
    await _create_novel(1)
    await _create_novel(2)
    await setup_fts()

    await create_entity(
        EntityCreate(novel_id=1, name="Alice", entity_type="character")
    )
    await create_entity(
        EntityCreate(novel_id=2, name="Alice", entity_type="location")
    )

    await rebuild_fts()

    results = await search_entities("Alice", novel_id=1)
    assert len(results) == 1
    assert results[0]["novel_id"] == 1


@pytest.mark.asyncio
async def test_search_no_results() -> None:
    await _create_novel(1)
    await setup_fts()

    await create_entity(
        EntityCreate(novel_id=1, name="Alice", entity_type="character")
    )
    await rebuild_fts()

    results = await search_entities("Nonexistent")
    assert len(results) == 0
