from __future__ import annotations

import pytest

from app.database import get_db_context
from app.kb.crud import create_entity
from app.kb.schemas import EntityCreate
from app.llm import FakeLLMProvider
from app.wiki.generator import (
    delete_wiki_page,
    generate_wiki,
    get_wiki_page,
    list_wiki_pages,
)
from app.wiki.schemas import WikiGenerateRequest

WIKI_RESPONSE = """# Alice

## Overview
Alice is a main character in the novel.

## Background
She was born in a small town and grew up to become a great adventurer.

## Relationships
- Bob: Best friend
- Charlie: Rival

## Notable Events
- Chapter 1: Introduction
- Chapter 5: Battle with the dragon
"""


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
async def test_generate_wiki() -> None:
    await _create_novel(1)
    entity = await create_entity(
        EntityCreate(novel_id=1, name="Alice", entity_type="character")
    )

    llm = FakeLLMProvider(responses=[WIKI_RESPONSE])
    request = WikiGenerateRequest(
        novel_id=1,
        entity_id=entity.id,
        language="en",
    )
    page = await generate_wiki(request, llm)

    assert page.novel_id == 1
    assert page.entity_id == entity.id
    assert page.title == "Alice"
    assert "Alice" in page.content
    assert page.version == 1
    assert page.language == "en"


@pytest.mark.asyncio
async def test_generate_wiki_version_increment() -> None:
    await _create_novel(1)
    entity = await create_entity(
        EntityCreate(novel_id=1, name="Bob", entity_type="character")
    )

    llm = FakeLLMProvider(responses=["Version 1", "Version 2"])

    request = WikiGenerateRequest(novel_id=1, entity_id=entity.id)
    page1 = await generate_wiki(request, llm)
    assert page1.version == 1

    page2 = await generate_wiki(request, llm)
    assert page2.version == 2


@pytest.mark.asyncio
async def test_get_wiki_page() -> None:
    await _create_novel(1)
    entity = await create_entity(
        EntityCreate(novel_id=1, name="Charlie", entity_type="character")
    )

    llm = FakeLLMProvider(responses=["Test content"])
    request = WikiGenerateRequest(novel_id=1, entity_id=entity.id)
    created = await generate_wiki(request, llm)

    fetched = await get_wiki_page(created.id)
    assert fetched is not None
    assert fetched.title == "Charlie"


@pytest.mark.asyncio
async def test_get_wiki_page_not_found() -> None:
    result = await get_wiki_page(99999)
    assert result is None


@pytest.mark.asyncio
async def test_list_wiki_pages() -> None:
    await _create_novel(1)
    entity = await create_entity(
        EntityCreate(novel_id=1, name="Dave", entity_type="character")
    )

    llm = FakeLLMProvider(responses=["Test"])
    request = WikiGenerateRequest(novel_id=1, entity_id=entity.id)
    await generate_wiki(request, llm)

    pages, total = await list_wiki_pages(novel_id=1)
    assert total == 1
    assert len(pages) == 1


@pytest.mark.asyncio
async def test_delete_wiki_page() -> None:
    await _create_novel(1)
    entity = await create_entity(
        EntityCreate(novel_id=1, name="Eve", entity_type="character")
    )

    llm = FakeLLMProvider(responses=["Test"])
    request = WikiGenerateRequest(novel_id=1, entity_id=entity.id)
    created = await generate_wiki(request, llm)

    deleted = await delete_wiki_page(created.id)
    assert deleted is True
    assert await get_wiki_page(created.id) is None


@pytest.mark.asyncio
async def test_generate_wiki_entity_not_found() -> None:
    await _create_novel(1)
    request = WikiGenerateRequest(novel_id=1, entity_id=99999)
    with pytest.raises(ValueError, match="Entity not found"):
        await generate_wiki(request)
