from __future__ import annotations

import aiosqlite

from ..database import get_db_context
from .schemas import (
    EntityCreate,
    EntityResponse,
    EntityUpdate,
    MergeRequest,
    parse_attributes,
    serialize_attributes,
)


def _normalize(text: str) -> str:
    return text.strip().lower()


async def create_entity(
    data: EntityCreate,
    db: aiosqlite.Connection | None = None,
) -> EntityResponse:
    managed = db is None
    ctx = get_db_context() if managed else None
    if ctx:
        db = await ctx.__aenter__()
    assert db is not None
    try:
        attrs_json = serialize_attributes(data.attributes)
        cursor = await db.execute(
            "INSERT INTO entities"
            " (novel_id, name, entity_type, attributes, source_chapter)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                data.novel_id, data.name, data.entity_type,
                attrs_json, data.source_chapter,
            ),
        )
        entity_id = cursor.lastrowid
        assert entity_id is not None

        normalized = _normalize(data.name)
        await db.execute(
            "INSERT INTO entity_aliases (entity_id, alias, normalized, is_primary)"
            " VALUES (?, ?, ?, 1)",
            (entity_id, data.name, normalized),
        )

        for alias in data.aliases:
            alias_norm = _normalize(alias)
            await db.execute(
                "INSERT INTO entity_aliases (entity_id, alias, normalized, is_primary)"
                " VALUES (?, ?, ?, 0)",
                (entity_id, alias, alias_norm),
            )

        await db.commit()
        return EntityResponse(
            id=entity_id,
            novel_id=data.novel_id,
            name=data.name,
            entity_type=data.entity_type,
            attributes=data.attributes,
            source_chapter=data.source_chapter,
            aliases=data.aliases,
            created_at="",
            updated_at="",
        )
    finally:
        if managed and ctx:
            await ctx.__aexit__(None, None, None)


async def get_entity(
    entity_id: int,
    db: aiosqlite.Connection | None = None,
) -> EntityResponse | None:
    managed = db is None
    ctx = get_db_context() if managed else None
    if ctx:
        db = await ctx.__aenter__()
    assert db is not None
    try:
        cursor = await db.execute(
            "SELECT id, novel_id, name, entity_type, attributes, source_chapter,"
            " created_at, updated_at FROM entities WHERE id = ?",
            (entity_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return None

        alias_cursor = await db.execute(
            "SELECT alias FROM entity_aliases WHERE entity_id = ? AND is_primary = 0"
            " ORDER BY alias",
            (entity_id,),
        )
        aliases = [r[0] for r in await alias_cursor.fetchall()]

        return EntityResponse(
            id=row[0],
            novel_id=row[1],
            name=row[2],
            entity_type=row[3],
            attributes=parse_attributes(row[4]),
            source_chapter=row[5],
            aliases=aliases,
            created_at=str(row[6]),
            updated_at=str(row[7]),
        )
    finally:
        if managed and ctx:
            await ctx.__aexit__(None, None, None)


async def list_entities(
    novel_id: int,
    entity_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: aiosqlite.Connection | None = None,
) -> tuple[list[EntityResponse], int]:
    managed = db is None
    ctx = get_db_context() if managed else None
    if ctx:
        db = await ctx.__aenter__()
    assert db is not None
    try:
        where = "WHERE novel_id = ?"
        params: list[object] = [novel_id]
        if entity_type:
            where += " AND entity_type = ?"
            params.append(entity_type)

        count_cursor = await db.execute(
            f"SELECT COUNT(*) FROM entities {where}", params
        )
        count_row = await count_cursor.fetchone()
        total = count_row[0] if count_row else 0

        cursor = await db.execute(
            f"SELECT id, novel_id, name, entity_type, attributes, source_chapter,"
            f" created_at, updated_at FROM entities {where}"
            f" ORDER BY name LIMIT ? OFFSET ?",
            [*params, limit, offset],
        )
        rows = await cursor.fetchall()

        entities = []
        for row in rows:
            alias_cursor = await db.execute(
                "SELECT alias FROM entity_aliases"
                " WHERE entity_id = ? AND is_primary = 0",
                (row[0],),
            )
            aliases = [r[0] for r in await alias_cursor.fetchall()]
            entities.append(
                EntityResponse(
                    id=row[0],
                    novel_id=row[1],
                    name=row[2],
                    entity_type=row[3],
                    attributes=parse_attributes(row[4]),
                    source_chapter=row[5],
                    aliases=aliases,
                    created_at=str(row[6]),
                    updated_at=str(row[7]),
                )
            )

        return entities, total
    finally:
        if managed and ctx:
            await ctx.__aexit__(None, None, None)


async def update_entity(
    entity_id: int,
    data: EntityUpdate,
    db: aiosqlite.Connection | None = None,
) -> EntityResponse | None:
    managed = db is None
    ctx = get_db_context() if managed else None
    if ctx:
        db = await ctx.__aenter__()
    assert db is not None
    try:
        updates = []
        params: list[object] = []
        if data.name is not None:
            updates.append("name = ?")
            params.append(data.name)
        if data.entity_type is not None:
            updates.append("entity_type = ?")
            params.append(data.entity_type)
        if data.attributes is not None:
            updates.append("attributes = ?")
            params.append(serialize_attributes(data.attributes))

        if not updates:
            return await get_entity(entity_id, db)

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(entity_id)

        await db.execute(
            f"UPDATE entities SET {', '.join(updates)} WHERE id = ?", params
        )
        await db.commit()

        return await get_entity(entity_id, db)
    finally:
        if managed and ctx:
            await ctx.__aexit__(None, None, None)


async def delete_entity(
    entity_id: int,
    db: aiosqlite.Connection | None = None,
) -> bool:
    managed = db is None
    ctx = get_db_context() if managed else None
    if ctx:
        db = await ctx.__aenter__()
    assert db is not None
    try:
        cursor = await db.execute("DELETE FROM entities WHERE id = ?", (entity_id,))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        if managed and ctx:
            await ctx.__aexit__(None, None, None)


async def resolve_alias(
    name: str,
    novel_id: int,
    db: aiosqlite.Connection | None = None,
) -> int | None:
    managed = db is None
    ctx = get_db_context() if managed else None
    if ctx:
        db = await ctx.__aenter__()
    assert db is not None
    try:
        normalized = _normalize(name)
        cursor = await db.execute(
            "SELECT ea.entity_id FROM entity_aliases ea"
            " JOIN entities e ON e.id = ea.entity_id"
            " WHERE ea.normalized = ? AND e.novel_id = ?",
            (normalized, novel_id),
        )
        row = await cursor.fetchone()
        return row[0] if row else None
    finally:
        if managed and ctx:
            await ctx.__aexit__(None, None, None)


async def merge_entities(
    data: MergeRequest,
    novel_id: int,
    db: aiosqlite.Connection | None = None,
) -> EntityResponse | None:
    managed = db is None
    ctx = get_db_context() if managed else None
    if ctx:
        db = await ctx.__aenter__()
    assert db is not None
    try:
        source = await get_entity(data.source_entity_id, db)
        target = await get_entity(data.target_entity_id, db)
        if not source or not target:
            return None

        keep_name = data.keep_name or target.name
        all_aliases = list(
            set([source.name] + source.aliases + [target.name] + target.aliases)
        )
        all_aliases = [a for a in all_aliases if a != keep_name]

        await db.execute(
            "UPDATE entity_mentions"
            " SET entity_id = ? WHERE entity_id = ?",
            (target.id, source.id),
        )
        await db.execute(
            "UPDATE entity_relationships"
            " SET source_entity_id = ? WHERE source_entity_id = ?",
            (target.id, source.id),
        )
        await db.execute(
            "UPDATE entity_relationships"
            " SET target_entity_id = ? WHERE target_entity_id = ?",
            (target.id, source.id),
        )
        await db.execute(
            "UPDATE wiki_pages SET entity_id = ? WHERE entity_id = ?",
            (target.id, source.id),
        )

        await db.execute(
            "UPDATE entities SET name = ?, attributes = json_patch(attributes, ?),"
            " updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (keep_name, serialize_attributes(source.attributes), target.id),
        )

        for alias in all_aliases:
            alias_norm = _normalize(alias)
            existing = await db.execute(
                "SELECT id FROM entity_aliases WHERE entity_id = ? AND normalized = ?",
                (target.id, alias_norm),
            )
            if not await existing.fetchone():
                await db.execute(
                    "INSERT INTO entity_aliases"
                    " (entity_id, alias, normalized, is_primary)"
                    " VALUES (?, ?, ?, 0)",
                    (target.id, alias, alias_norm),
                )

        await db.execute("DELETE FROM entities WHERE id = ?", (source.id,))
        await db.commit()

        return await get_entity(target.id, db)
    finally:
        if managed and ctx:
            await ctx.__aexit__(None, None, None)
