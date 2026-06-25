from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

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


@router.post("/tools/{tool_name}")
async def execute_tool_endpoint(
    tool_name: str, arguments: dict[str, object]
) -> dict[str, object]:
    result = await execute_tool(tool_name, arguments)
    return result
