from __future__ import annotations

import pytest

from app.database import get_db_context
from app.export import export_novel_json, export_novel_markdown, export_wiki_markdown


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
        await db.execute(
            "INSERT INTO chapters (novel_id, chapter_number, title, content)"
            " VALUES (?, ?, ?, ?)",
            (novel_id, 1, "Chapter 1", "Content of chapter 1"),
        )
        await db.commit()


@pytest.mark.asyncio
async def test_export_novel_markdown() -> None:
    await _create_novel(1)
    content = await export_novel_markdown(novel_id=1)
    assert "# Test Novel 1" in content
    assert "Chapter 1" in content
    assert "Content of chapter 1" in content


@pytest.mark.asyncio
async def test_export_novel_json() -> None:
    await _create_novel(1)
    data = await export_novel_json(novel_id=1)
    assert "novel" in data
    assert "chapters" in data
    novel = data["novel"]
    assert isinstance(novel, dict)
    assert novel["title"] == "Test Novel 1"
    chapters = data["chapters"]
    assert isinstance(chapters, list)
    assert len(chapters) == 1


@pytest.mark.asyncio
async def test_export_wiki_markdown() -> None:
    await _create_novel(1)
    content = await export_wiki_markdown(novel_id=1)
    assert "# Wiki Export" in content


@pytest.mark.asyncio
async def test_export_novel_not_found() -> None:
    with pytest.raises(ValueError, match="Novel not found"):
        await export_novel_markdown(novel_id=99999)
