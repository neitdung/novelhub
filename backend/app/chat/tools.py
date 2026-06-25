from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..kb.crud import get_entity, list_entities, resolve_alias
from ..search import search_entities, search_wiki
from ..wiki.generator import get_wiki_page

ToolFunc = Callable[..., Any]

TOOL_REGISTRY: dict[str, ToolFunc] = {}


def register_tool(name: str) -> Callable[[ToolFunc], ToolFunc]:
    def decorator(func: ToolFunc) -> ToolFunc:
        TOOL_REGISTRY[name] = func
        return func
    return decorator


@register_tool("search_entities")
async def tool_search_entities(
    query: str, novel_id: int | None = None
) -> list[dict[str, Any]]:
    results = await search_entities(query, novel_id)
    return [
        {"id": r["id"], "name": r["name"], "type": r["entity_type"]}
        for r in results
    ]


@register_tool("search_wiki")
async def tool_search_wiki(
    query: str, novel_id: int | None = None
) -> list[dict[str, Any]]:
    results = await search_wiki(query, novel_id)
    return [
        {"id": r["id"], "title": r["title"], "language": r["language"]}
        for r in results
    ]


@register_tool("get_entity")
async def tool_get_entity(entity_id: int) -> dict[str, Any] | None:
    entity = await get_entity(entity_id)
    if not entity:
        return None
    return {
        "id": entity.id,
        "name": entity.name,
        "type": entity.entity_type,
        "aliases": entity.aliases,
        "attributes": entity.attributes,
    }


@register_tool("resolve_alias")
async def tool_resolve_alias(
    name: str, novel_id: int
) -> dict[str, Any] | None:
    entity_id = await resolve_alias(name, novel_id)
    if not entity_id:
        return None
    entity = await get_entity(entity_id)
    if not entity:
        return None
    return {
        "id": entity.id,
        "name": entity.name,
        "type": entity.entity_type,
    }


@register_tool("get_wiki_page")
async def tool_get_wiki_page(page_id: int) -> dict[str, Any] | None:
    page = await get_wiki_page(page_id)
    if not page:
        return None
    return {
        "id": page.id,
        "title": page.title,
        "content": page.content,
        "language": page.language,
        "version": page.version,
    }


@register_tool("list_entities")
async def tool_list_entities(
    novel_id: int, entity_type: str | None = None
) -> list[dict[str, Any]]:
    entities, _ = await list_entities(novel_id, entity_type, limit=50)
    return [{"id": e.id, "name": e.name, "type": e.entity_type} for e in entities]


async def execute_tool(
    tool_name: str, arguments: dict[str, Any]
) -> dict[str, Any]:
    if tool_name not in TOOL_REGISTRY:
        return {"error": f"Unknown tool: {tool_name}"}

    try:
        func = TOOL_REGISTRY[tool_name]
        result = await func(**arguments)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}


def get_available_tools() -> list[dict[str, str]]:
    return [
        {"name": name, "description": func.__doc__ or ""}
        for name, func in TOOL_REGISTRY.items()
    ]
