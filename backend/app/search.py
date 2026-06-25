from __future__ import annotations

from .database import get_db_context


async def setup_fts() -> None:
    async with get_db_context() as db:
        await db.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS entities_fts USING fts5(
                name, entity_type, aliases
            )
        """)

        await db.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS wiki_pages_fts USING fts5(
                title, content
            )
        """)

        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS entities_ai AFTER INSERT ON entities BEGIN
                INSERT INTO entities_fts(rowid, name, entity_type, aliases)
                VALUES (new.id, new.name, new.entity_type, '');
            END
        """)

        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS entities_ad
            AFTER DELETE ON entities BEGIN
                INSERT INTO entities_fts(
                    entities_fts, rowid, name, entity_type, aliases
                )
                VALUES (
                    'delete', old.id, old.name, old.entity_type, ''
                );
            END
        """)

        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS entities_au
            AFTER UPDATE ON entities BEGIN
                INSERT INTO entities_fts(
                    entities_fts, rowid, name, entity_type, aliases
                )
                VALUES (
                    'delete', old.id, old.name, old.entity_type, ''
                );
                INSERT INTO entities_fts(
                    rowid, name, entity_type, aliases
                )
                VALUES (new.id, new.name, new.entity_type, '');
            END
        """)

        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS wiki_pages_ai
            AFTER INSERT ON wiki_pages BEGIN
                INSERT INTO wiki_pages_fts(rowid, title, content)
                VALUES (new.id, new.title, new.content);
            END
        """)

        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS wiki_pages_ad
            AFTER DELETE ON wiki_pages BEGIN
                INSERT INTO wiki_pages_fts(
                    wiki_pages_fts, rowid, title, content
                )
                VALUES ('delete', old.id, old.title, old.content);
            END
        """)

        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS wiki_pages_au
            AFTER UPDATE ON wiki_pages BEGIN
                INSERT INTO wiki_pages_fts(
                    wiki_pages_fts, rowid, title, content
                )
                VALUES ('delete', old.id, old.title, old.content);
                INSERT INTO wiki_pages_fts(rowid, title, content)
                VALUES (new.id, new.title, new.content);
            END
        """)

        await db.commit()


async def rebuild_fts() -> None:
    async with get_db_context() as db:
        await db.execute("DROP TABLE IF EXISTS entities_fts")
        await db.execute("DROP TABLE IF EXISTS wiki_pages_fts")
        await db.commit()
    await setup_fts()
    async with get_db_context() as db:
        cursor = await db.execute("SELECT id, name, entity_type FROM entities")
        rows = await cursor.fetchall()
        for row in rows:
            await db.execute(
                "INSERT INTO entities_fts(rowid, name, entity_type, aliases)"
                " VALUES (?, ?, ?, '')",
                (row[0], row[1], row[2]),
            )

        cursor = await db.execute("SELECT id, title, content FROM wiki_pages")
        rows = await cursor.fetchall()
        for row in rows:
            await db.execute(
                "INSERT INTO wiki_pages_fts(rowid, title, content) VALUES (?, ?, ?)",
                (row[0], row[1], row[2]),
            )

        await db.commit()


async def search_entities(
    query: str,
    novel_id: int | None = None,
    limit: int = 20,
) -> list[dict[str, object]]:
    async with get_db_context() as db:
        sql = """
            SELECT e.id, e.novel_id, e.name, e.entity_type, e.attributes,
                   rank
            FROM entities_fts fts
            JOIN entities e ON e.id = fts.rowid
            WHERE entities_fts MATCH ?
        """
        params: list[object] = [query]

        if novel_id is not None:
            sql += " AND e.novel_id = ?"
            params.append(novel_id)

        sql += " ORDER BY rank LIMIT ?"
        params.append(limit)

        cursor = await db.execute(sql, params)
        rows = await cursor.fetchall()

        return [
            {
                "id": r[0],
                "novel_id": r[1],
                "name": r[2],
                "entity_type": r[3],
                "attributes": r[4],
                "rank": r[5],
            }
            for r in rows
        ]


async def search_wiki(
    query: str,
    novel_id: int | None = None,
    limit: int = 20,
) -> list[dict[str, object]]:
    async with get_db_context() as db:
        sql = """
            SELECT w.id, w.novel_id, w.title, w.language, w.version, rank
            FROM wiki_pages_fts fts
            JOIN wiki_pages w ON w.id = fts.rowid
            WHERE wiki_pages_fts MATCH ?
        """
        params: list[object] = [query]

        if novel_id is not None:
            sql += " AND w.novel_id = ?"
            params.append(novel_id)

        sql += " ORDER BY rank LIMIT ?"
        params.append(limit)

        cursor = await db.execute(sql, params)
        rows = await cursor.fetchall()

        return [
            {
                "id": r[0],
                "novel_id": r[1],
                "title": r[2],
                "language": r[3],
                "version": r[4],
                "rank": r[5],
            }
            for r in rows
        ]
