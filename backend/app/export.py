from __future__ import annotations

import json

from .database import get_db_context


async def export_novel_markdown(novel_id: int) -> str:
    async with get_db_context() as db:
        cursor = await db.execute(
            "SELECT title, author, language FROM novels WHERE id = ?",
            (novel_id,),
        )
        novel = await cursor.fetchone()
        if not novel:
            raise ValueError("Novel not found")

        cursor = await db.execute(
            "SELECT chapter_number, title, content FROM chapters"
            " WHERE novel_id = ? ORDER BY chapter_number",
            (novel_id,),
        )
        chapters = list(await cursor.fetchall())

        lines = [
            f"# {novel[0]}",
            "",
            f"**Author:** {novel[1]}",
            f"**Language:** {novel[2]}",
            f"**Chapters:** {len(chapters)}",
            "",
            "---",
            "",
        ]

        for ch in chapters:
            ch_title = ch[1] or f"Chapter {ch[0]}"
            lines.append(f"## {ch_title}")
            lines.append("")
            lines.append(ch[2] or "")
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)


async def export_novel_json(novel_id: int) -> dict[str, object]:
    async with get_db_context() as db:
        cursor = await db.execute(
            "SELECT id, title, author, language, file_hash,"
            " created_at, updated_at FROM novels WHERE id = ?",
            (novel_id,),
        )
        novel = await cursor.fetchone()
        if not novel:
            raise ValueError("Novel not found")

        cursor = await db.execute(
            "SELECT chapter_number, title, content FROM chapters"
            " WHERE novel_id = ? ORDER BY chapter_number",
            (novel_id,),
        )
        chapters = [
            {"number": r[0], "title": r[1], "content": r[2]}
            for r in await cursor.fetchall()
        ]

        cursor = await db.execute(
            "SELECT name, entity_type, attributes FROM entities"
            " WHERE novel_id = ? ORDER BY name",
            (novel_id,),
        )
        entities = [
            {"name": r[0], "type": r[1], "attributes": json.loads(r[2] or "{}")}
            for r in await cursor.fetchall()
        ]

        return {
            "novel": {
                "id": novel[0],
                "title": novel[1],
                "author": novel[2],
                "language": novel[3],
                "file_hash": novel[4],
                "created_at": str(novel[5]),
                "updated_at": str(novel[6]),
            },
            "chapters": chapters,
            "entities": entities,
        }


async def export_wiki_markdown(novel_id: int) -> str:
    async with get_db_context() as db:
        cursor = await db.execute(
            "SELECT title, content, language, version FROM wiki_pages"
            " WHERE novel_id = ? AND is_published = 1"
            " ORDER BY title",
            (novel_id,),
        )
        pages = list(await cursor.fetchall())

        lines = [
            "# Wiki Export",
            "",
            f"**Pages:** {len(pages)}",
            "",
            "---",
            "",
        ]

        for page in pages:
            lines.append(f"## {page[0]}")
            lines.append("")
            lines.append(f"*Language: {page[2]} | Version: {page[3]}*")
            lines.append("")
            lines.append(page[1])
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)
