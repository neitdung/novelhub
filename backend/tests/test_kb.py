from __future__ import annotations

import pytest

from app.database import get_db_context
from app.kb.crud import (
    create_entity,
    delete_entity,
    get_entity,
    list_entities,
    merge_entities,
    resolve_alias,
    update_entity,
)
from app.kb.schemas import EntityCreate, EntityUpdate, MergeRequest


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
async def test_create_entity() -> None:
    await _create_novel(1)
    data = EntityCreate(
        novel_id=1,
        name="Alice",
        entity_type="character",
        aliases=["Alicia", "Ali"],
    )
    entity = await create_entity(data)
    assert entity.name == "Alice"
    assert entity.entity_type == "character"
    assert entity.novel_id == 1
    assert "Alicia" in entity.aliases
    assert "Ali" in entity.aliases


@pytest.mark.asyncio
async def test_get_entity() -> None:
    await _create_novel(1)
    data = EntityCreate(novel_id=1, name="Bob", entity_type="character")
    created = await create_entity(data)
    fetched = await get_entity(created.id)
    assert fetched is not None
    assert fetched.name == "Bob"


@pytest.mark.asyncio
async def test_get_entity_not_found() -> None:
    result = await get_entity(99999)
    assert result is None


@pytest.mark.asyncio
async def test_list_entities() -> None:
    await _create_novel(2)
    await create_entity(EntityCreate(novel_id=2, name="X", entity_type="location"))
    await create_entity(EntityCreate(novel_id=2, name="Y", entity_type="character"))
    entities, total = await list_entities(novel_id=2)
    assert total == 2
    assert len(entities) == 2


@pytest.mark.asyncio
async def test_list_entities_with_type_filter() -> None:
    await _create_novel(3)
    await create_entity(EntityCreate(novel_id=3, name="A", entity_type="character"))
    await create_entity(EntityCreate(novel_id=3, name="B", entity_type="location"))
    entities, total = await list_entities(novel_id=3, entity_type="character")
    assert total == 1
    assert entities[0].name == "A"


@pytest.mark.asyncio
async def test_update_entity() -> None:
    await _create_novel(1)
    data = EntityCreate(novel_id=1, name="Old Name", entity_type="character")
    created = await create_entity(data)
    updated = await update_entity(
        created.id, EntityUpdate(name="New Name")
    )
    assert updated is not None
    assert updated.name == "New Name"


@pytest.mark.asyncio
async def test_delete_entity() -> None:
    await _create_novel(1)
    data = EntityCreate(novel_id=1, name="ToDelete", entity_type="character")
    created = await create_entity(data)
    deleted = await delete_entity(created.id)
    assert deleted is True
    assert await get_entity(created.id) is None


@pytest.mark.asyncio
async def test_resolve_alias() -> None:
    await _create_novel(5)
    data = EntityCreate(
        novel_id=5, name="Primary", aliases=["Alt1", "Alt2"]
    )
    await create_entity(data)
    entity_id = await resolve_alias("Alt1", novel_id=5)
    assert entity_id is not None
    entity_id = await resolve_alias("primary", novel_id=5)
    assert entity_id is not None
    entity_id = await resolve_alias("nonexistent", novel_id=5)
    assert entity_id is None


@pytest.mark.asyncio
async def test_merge_entities() -> None:
    await _create_novel(6)
    src = await create_entity(
        EntityCreate(
            novel_id=6, name="Source", entity_type="character",
            aliases=["SrcAlias"],
        )
    )
    tgt = await create_entity(
        EntityCreate(
            novel_id=6, name="Target", entity_type="character",
            aliases=["TgtAlias"],
        )
    )
    result = await merge_entities(
        MergeRequest(
            source_entity_id=src.id,
            target_entity_id=tgt.id,
            keep_name="Merged",
        ),
        novel_id=6,
    )
    assert result is not None
    assert result.name == "Merged"
    assert await get_entity(src.id) is None


@pytest.mark.asyncio
async def test_alias_case_insensitive() -> None:
    await _create_novel(7)
    data = EntityCreate(novel_id=7, name="Alice", entity_type="character")
    await create_entity(data)
    entity_id = await resolve_alias("ALICE", novel_id=7)
    assert entity_id is not None
    entity_id = await resolve_alias("alice", novel_id=7)
    assert entity_id is not None
