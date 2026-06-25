from __future__ import annotations

import json

from pydantic import BaseModel


class ConversationCreate(BaseModel):
    novel_id: int
    title: str = "New Chat"


class ConversationResponse(BaseModel):
    id: int
    novel_id: int
    title: str
    created_at: str
    updated_at: str


class ConversationList(BaseModel):
    conversations: list[ConversationResponse]
    total: int


class MessageCreate(BaseModel):
    role: str = "user"
    content: str = ""
    citations: list[dict[str, object]] = []
    tool_calls: list[dict[str, object]] = []


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    citations: list[dict[str, object]]
    tool_calls: list[dict[str, object]]
    created_at: str


class MessageList(BaseModel):
    messages: list[MessageResponse]
    total: int


class ToolCall(BaseModel):
    tool: str
    arguments: dict[str, object]


class ToolResult(BaseModel):
    tool: str
    result: object
    error: str | None = None


def parse_citations(raw: str | None) -> list[dict[str, object]]:
    if not raw:
        return []
    try:
        result = json.loads(raw)
        if isinstance(result, list):
            return result
    except (json.JSONDecodeError, TypeError):
        pass
    return []


def serialize_citations(citations: list[dict[str, object]]) -> str:
    return json.dumps(citations, ensure_ascii=False)


def parse_tool_calls(raw: str | None) -> list[dict[str, object]]:
    if not raw:
        return []
    try:
        result = json.loads(raw)
        if isinstance(result, list):
            return result
    except (json.JSONDecodeError, TypeError):
        pass
    return []


def serialize_tool_calls(tool_calls: list[dict[str, object]]) -> str:
    return json.dumps(tool_calls, ensure_ascii=False)
