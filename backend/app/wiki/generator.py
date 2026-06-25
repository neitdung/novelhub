from __future__ import annotations

import json

from ..database import get_db_context
from ..kb.crud import get_entity
from ..llm import FakeLLMProvider
from ..llm.base import LLMProvider
from .schemas import WikiGenerateRequest, WikiPageResponse

WIKI_PROMPT = """Generate a wiki page for the following entity from a novel.

Entity: {name} (Type: {entity_type})
Aliases: {aliases}
Attributes: {attributes}

Generate a comprehensive wiki article including:
1. Overview/Description
2. Background and history
3. Key relationships
4. Notable events involving this entity
5. Trivia or additional notes

Return the content in {language} as Markdown.

Chapter evidence references:
{chapter_evidence}"""


async def generate_wiki(
    request: WikiGenerateRequest,
    llm: LLMProvider | None = None,
) -> WikiPageResponse:
    if llm is None:
        llm = FakeLLMProvider()

    async with get_db_context() as db:
        if request.entity_id:
            entity = await get_entity(request.entity_id, db)
            if not entity:
                raise ValueError("Entity not found")

            title = request.title or entity.name
            entity_info = {
                "name": entity.name,
                "type": entity.entity_type,
                "aliases": entity.aliases,
                "attributes": entity.attributes,
            }

            cursor = await db.execute(
                "SELECT chapter_id FROM entity_mentions"
                " WHERE entity_id = ? ORDER BY chapter_id",
                (request.entity_id,),
            )
            chapters = [r[0] for r in await cursor.fetchall()]
        else:
            entity_info = {
                "name": request.title or "Untitled",
                "type": "topic",
                "aliases": [],
                "attributes": {},
            }
            title = request.title or "Untitled"
            chapters = []

        aliases_str = (
            ", ".join(entity_info["aliases"])
            if entity_info["aliases"]
            else "None"
        )
        attrs_str = json.dumps(
            entity_info["attributes"], ensure_ascii=False
        )
        chapter_lines = (
            [f"- Chapter {c}" for c in chapters]
            if chapters
            else ["No chapter evidence available"]
        )

        prompt = WIKI_PROMPT.format(
            name=entity_info["name"],
            entity_type=entity_info["type"],
            aliases=aliases_str,
            attributes=attrs_str,
            language=request.language,
            chapter_evidence="\n".join(chapter_lines),
        )

        response = await llm.complete(
            [{"role": "user", "content": prompt}]
        )
        content = response.content

        cursor = await db.execute(
            "SELECT version FROM wiki_pages"
            " WHERE novel_id = ? AND entity_id = ?"
            " AND language = ? AND prompt_version = ?"
            " ORDER BY version DESC LIMIT 1",
            (
                request.novel_id,
                request.entity_id,
                request.language,
                request.prompt_version,
            ),
        )
        existing = await cursor.fetchone()
        version = (existing[0] + 1) if existing else 1

        cursor = await db.execute(
            "INSERT INTO wiki_pages"
            " (novel_id, entity_id, title, content, language,"
            " version, source_chapters, prompt_version, is_published)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)",
            (
                request.novel_id,
                request.entity_id,
                title,
                content,
                request.language,
                version,
                json.dumps(chapters),
                request.prompt_version,
            ),
        )
        page_id = cursor.lastrowid
        assert page_id is not None
        await db.commit()

        return WikiPageResponse(
            id=page_id,
            novel_id=request.novel_id,
            entity_id=request.entity_id,
            title=title,
            content=content,
            language=request.language,
            version=version,
            source_chapters=chapters,
            prompt_version=request.prompt_version,
            is_published=False,
            created_at="",
            updated_at="",
        )


async def get_wiki_page(page_id: int) -> WikiPageResponse | None:
    async with get_db_context() as db:
        cursor = await db.execute(
            "SELECT id, novel_id, entity_id, title, content, language,"
            " version, source_chapters, prompt_version, is_published,"
            " created_at, updated_at FROM wiki_pages WHERE id = ?",
            (page_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return None

        return WikiPageResponse(
            id=row[0],
            novel_id=row[1],
            entity_id=row[2],
            title=row[3],
            content=row[4],
            language=row[5],
            version=row[6],
            source_chapters=json.loads(row[7]) if row[7] else [],
            prompt_version=row[8],
            is_published=bool(row[9]),
            created_at=str(row[10]),
            updated_at=str(row[11]),
        )


async def list_wiki_pages(
    novel_id: int,
    entity_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[WikiPageResponse], int]:
    async with get_db_context() as db:
        where = "WHERE novel_id = ?"
        params: list[object] = [novel_id]
        if entity_id is not None:
            where += " AND entity_id = ?"
            params.append(entity_id)

        count_cursor = await db.execute(
            f"SELECT COUNT(*) FROM wiki_pages {where}", params
        )
        count_row = await count_cursor.fetchone()
        total = count_row[0] if count_row else 0

        cursor = await db.execute(
            f"SELECT id, novel_id, entity_id, title, content, language,"
            f" version, source_chapters, prompt_version, is_published,"
            f" created_at, updated_at FROM wiki_pages {where}"
            f" ORDER BY title LIMIT ? OFFSET ?",
            [*params, limit, offset],
        )
        rows = await cursor.fetchall()

        pages = [
            WikiPageResponse(
                id=r[0],
                novel_id=r[1],
                entity_id=r[2],
                title=r[3],
                content=r[4],
                language=r[5],
                version=r[6],
                source_chapters=json.loads(r[7]) if r[7] else [],
                prompt_version=r[8],
                is_published=bool(r[9]),
                created_at=str(r[10]),
                updated_at=str(r[11]),
            )
            for r in rows
        ]

        return pages, total


async def delete_wiki_page(page_id: int) -> bool:
    async with get_db_context() as db:
        cursor = await db.execute(
            "DELETE FROM wiki_pages WHERE id = ?", (page_id,)
        )
        await db.commit()
        return cursor.rowcount > 0
