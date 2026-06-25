from __future__ import annotations

import json

from pydantic import BaseModel


class EntityCreate(BaseModel):
    novel_id: int
    name: str
    entity_type: str = "character"
    attributes: dict[str, object] = {}
    source_chapter: int | None = None
    aliases: list[str] = []


class EntityUpdate(BaseModel):
    name: str | None = None
    entity_type: str | None = None
    attributes: dict[str, object] | None = None


class EntityResponse(BaseModel):
    id: int
    novel_id: int
    name: str
    entity_type: str
    attributes: dict[str, object]
    source_chapter: int | None
    aliases: list[str]
    created_at: str
    updated_at: str


class EntityList(BaseModel):
    entities: list[EntityResponse]
    total: int


class MergeRequest(BaseModel):
    source_entity_id: int
    target_entity_id: int
    keep_name: str | None = None


class AliasCreate(BaseModel):
    alias: str
    is_primary: bool = False


class MentionCreate(BaseModel):
    chapter_id: int
    position: int = 0
    context: str | None = None


class RelationshipCreate(BaseModel):
    novel_id: int
    source_entity_id: int
    target_entity_id: int
    relationship_type: str = "related_to"
    attributes: dict[str, object] = {}
    source_chapter: int | None = None


def parse_attributes(raw: str | None) -> dict[str, object]:
    if not raw:
        return {}
    try:
        result = json.loads(raw)
        if isinstance(result, dict):
            return result
    except (json.JSONDecodeError, TypeError):
        pass
    return {}


def serialize_attributes(attrs: dict[str, object]) -> str:
    return json.dumps(attrs, ensure_ascii=False)
