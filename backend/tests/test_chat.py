from __future__ import annotations

import pytest

from app.chat.crud import (
    add_message,
    create_conversation,
    delete_conversation,
    get_conversation,
    list_conversations,
    list_messages,
)
from app.chat.schemas import ConversationCreate, MessageCreate
from app.database import get_db_context


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
async def test_create_conversation() -> None:
    await _create_novel(1)
    data = ConversationCreate(novel_id=1, title="Test Chat")
    conv = await create_conversation(data)
    assert conv.title == "Test Chat"
    assert conv.novel_id == 1


@pytest.mark.asyncio
async def test_get_conversation() -> None:
    await _create_novel(1)
    data = ConversationCreate(novel_id=1, title="Get Chat")
    created = await create_conversation(data)
    fetched = await get_conversation(created.id)
    assert fetched is not None
    assert fetched.title == "Get Chat"


@pytest.mark.asyncio
async def test_get_conversation_not_found() -> None:
    result = await get_conversation(99999)
    assert result is None


@pytest.mark.asyncio
async def test_list_conversations() -> None:
    await _create_novel(1)
    await create_conversation(ConversationCreate(novel_id=1, title="Chat 1"))
    await create_conversation(ConversationCreate(novel_id=1, title="Chat 2"))
    convs, total = await list_conversations(novel_id=1)
    assert total == 2
    assert len(convs) == 2


@pytest.mark.asyncio
async def test_delete_conversation() -> None:
    await _create_novel(1)
    data = ConversationCreate(novel_id=1, title="Delete Me")
    created = await create_conversation(data)
    deleted = await delete_conversation(created.id)
    assert deleted is True
    assert await get_conversation(created.id) is None


@pytest.mark.asyncio
async def test_add_message() -> None:
    await _create_novel(1)
    conv = await create_conversation(ConversationCreate(novel_id=1))
    data = MessageCreate(role="user", content="Hello")
    msg = await add_message(conv.id, data)
    assert msg.role == "user"
    assert msg.content == "Hello"


@pytest.mark.asyncio
async def test_list_messages() -> None:
    await _create_novel(1)
    conv = await create_conversation(ConversationCreate(novel_id=1))
    await add_message(conv.id, MessageCreate(role="user", content="Hi"))
    await add_message(conv.id, MessageCreate(role="assistant", content="Hello!"))
    messages, total = await list_messages(conv.id)
    assert total == 2
    assert len(messages) == 2
