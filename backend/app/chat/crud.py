from __future__ import annotations

from ..database import get_db_context
from .schemas import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    parse_citations,
    parse_tool_calls,
    serialize_citations,
    serialize_tool_calls,
)


async def create_conversation(
    data: ConversationCreate,
) -> ConversationResponse:
    async with get_db_context() as db:
        cursor = await db.execute(
            "INSERT INTO conversations (novel_id, title) VALUES (?, ?)",
            (data.novel_id, data.title),
        )
        conv_id = cursor.lastrowid
        assert conv_id is not None
        await db.commit()

        return ConversationResponse(
            id=conv_id,
            novel_id=data.novel_id,
            title=data.title,
            created_at="",
            updated_at="",
        )


async def get_conversation(
    conv_id: int,
) -> ConversationResponse | None:
    async with get_db_context() as db:
        cursor = await db.execute(
            "SELECT id, novel_id, title, created_at, updated_at"
            " FROM conversations WHERE id = ?",
            (conv_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return None

        return ConversationResponse(
            id=row[0],
            novel_id=row[1],
            title=row[2],
            created_at=str(row[3]),
            updated_at=str(row[4]),
        )


async def list_conversations(
    novel_id: int,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[ConversationResponse], int]:
    async with get_db_context() as db:
        count_cursor = await db.execute(
            "SELECT COUNT(*) FROM conversations WHERE novel_id = ?",
            (novel_id,),
        )
        count_row = await count_cursor.fetchone()
        total = count_row[0] if count_row else 0

        cursor = await db.execute(
            "SELECT id, novel_id, title, created_at, updated_at"
            " FROM conversations WHERE novel_id = ?"
            " ORDER BY updated_at DESC LIMIT ? OFFSET ?",
            (novel_id, limit, offset),
        )
        rows = await cursor.fetchall()

        conversations = [
            ConversationResponse(
                id=r[0],
                novel_id=r[1],
                title=r[2],
                created_at=str(r[3]),
                updated_at=str(r[4]),
            )
            for r in rows
        ]

        return conversations, total


async def delete_conversation(conv_id: int) -> bool:
    async with get_db_context() as db:
        cursor = await db.execute(
            "DELETE FROM conversations WHERE id = ?", (conv_id,)
        )
        await db.commit()
        return cursor.rowcount > 0


async def add_message(
    conv_id: int,
    data: MessageCreate,
) -> MessageResponse:
    async with get_db_context() as db:
        citations_json = serialize_citations(data.citations)
        tool_calls_json = serialize_tool_calls(data.tool_calls)

        cursor = await db.execute(
            "INSERT INTO messages"
            " (conversation_id, role, content, citations, tool_calls)"
            " VALUES (?, ?, ?, ?, ?)",
            (conv_id, data.role, data.content, citations_json, tool_calls_json),
        )
        msg_id = cursor.lastrowid
        assert msg_id is not None

        await db.execute(
            "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP"
            " WHERE id = ?",
            (conv_id,),
        )
        await db.commit()

        return MessageResponse(
            id=msg_id,
            conversation_id=conv_id,
            role=data.role,
            content=data.content,
            citations=data.citations,
            tool_calls=data.tool_calls,
            created_at="",
        )


async def list_messages(
    conv_id: int,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[MessageResponse], int]:
    async with get_db_context() as db:
        count_cursor = await db.execute(
            "SELECT COUNT(*) FROM messages WHERE conversation_id = ?",
            (conv_id,),
        )
        count_row = await count_cursor.fetchone()
        total = count_row[0] if count_row else 0

        cursor = await db.execute(
            "SELECT id, conversation_id, role, content, citations,"
            " tool_calls, created_at FROM messages"
            " WHERE conversation_id = ?"
            " ORDER BY created_at ASC LIMIT ? OFFSET ?",
            (conv_id, limit, offset),
        )
        rows = await cursor.fetchall()

        messages = [
            MessageResponse(
                id=r[0],
                conversation_id=r[1],
                role=r[2],
                content=r[3],
                citations=parse_citations(r[4]),
                tool_calls=parse_tool_calls(r[5]),
                created_at=str(r[6]),
            )
            for r in rows
        ]

        return messages, total
