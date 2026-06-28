from __future__ import annotations

import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from ..chat.crud import (
    add_message,
    create_conversation,
    delete_conversation,
    get_conversation,
    list_conversations,
    list_messages,
)
from ..chat.schemas import (
    ConversationCreate,
    ConversationList,
    ConversationResponse,
    MessageCreate,
    MessageList,
    MessageResponse,
)
from ..chat.tools import execute_tool, get_available_tools
from ..llm import get_llm_provider
from ..llm.base import LLMProvider

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation_endpoint(
    data: ConversationCreate,
) -> ConversationResponse:
    return await create_conversation(data)


@router.get("/conversations", response_model=ConversationList)
async def list_conversations_endpoint(
    novel_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> ConversationList:
    conversations, total = await list_conversations(novel_id, limit, offset)
    return ConversationList(conversations=conversations, total=total)


@router.get("/conversations/{conv_id}", response_model=ConversationResponse)
async def get_conversation_endpoint(
    conv_id: int,
) -> ConversationResponse:
    conv = await get_conversation(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.delete("/conversations/{conv_id}")
async def delete_conversation_endpoint(conv_id: int) -> dict[str, str]:
    deleted = await delete_conversation(conv_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted"}


@router.post(
    "/conversations/{conv_id}/messages",
    response_model=MessageResponse,
    status_code=201,
)
async def add_message_endpoint(
    conv_id: int, data: MessageCreate
) -> MessageResponse:
    conv = await get_conversation(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return await add_message(conv_id, data)


@router.get("/conversations/{conv_id}/messages", response_model=MessageList)
async def list_messages_endpoint(
    conv_id: int,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> MessageList:
    messages, total = await list_messages(conv_id, limit, offset)
    return MessageList(messages=messages, total=total)


@router.get("/tools")
async def list_tools_endpoint() -> list[dict[str, str]]:
    return get_available_tools()


async def _generate_stream(
    conv_id: int,
    messages: list[dict[str, str]],
    llm: LLMProvider,
) -> AsyncGenerator[str, None]:
    """Generate SSE events for streaming LLM responses."""
    full_response = ""
    try:
        response = await llm.complete(messages)
        content = response.content
        full_response = content

        # Yield the complete response as a single chunk for simplicity
        # In production, this would use a true streaming API
        yield f"data: {json.dumps({'type': 'chunk', 'content': content})}\n\n"
        yield f"data: {json.dumps({'type': 'done', 'content': full_response})}\n\n"

    except Exception as e:
        error_msg = f"Streaming error: {e}"
        yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"

    finally:
        # Save the assistant message to the conversation
        if full_response:
            await add_message(
                conv_id,
                MessageCreate(
                    role="assistant",
                    content=full_response,
                    citations=[],
                    tool_calls=[],
                ),
            )


@router.post("/conversations/{conv_id}/stream")
async def stream_chat_response(conv_id: int, request: Request) -> StreamingResponse:
    """Stream a chat response using SSE from a user message."""
    conv = await get_conversation(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    body = await request.json()
    user_content = body.get("content", "") if isinstance(body, dict) else ""
    tool_name = body.get("tool") if isinstance(body, dict) else None
    tool_args = body.get("arguments", {}) if isinstance(body, dict) else {}

    # Save the user message
    await add_message(
        conv_id,
        MessageCreate(
            role="user",
            content=user_content,
            citations=[],
            tool_calls=[],
        ),
    )

    # Get conversation history
    existing_messages, _ = await list_messages(conv_id, limit=50, offset=0)
    history: list[dict[str, str]] = []
    for msg in existing_messages:
        role = "assistant" if msg.role == "assistant" else "user"
        history.append({"role": role, "content": msg.content})

    # Handle tool execution if requested
    if tool_name:
        tool_result = await execute_tool(tool_name, tool_args)
        result_content = json.dumps(tool_result, ensure_ascii=False)
        tool_msg = f"Tool {tool_name} returned: {result_content}"
        history.append({"role": "user", "content": tool_msg})

    llm = get_llm_provider()

    return StreamingResponse(
        _generate_stream(conv_id, history, llm),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/tools/{tool_name}")
async def execute_tool_endpoint(
    tool_name: str, arguments: dict[str, object]
) -> dict[str, object]:
    result = await execute_tool(tool_name, arguments)
    return result
