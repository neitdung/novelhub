from __future__ import annotations

from fastapi import APIRouter, Query

from ..search import search_entities, search_wiki

router = APIRouter(prefix="/api/search", tags=["search"])


class SearchResult:
    def __init__(
        self,
        entities: list[dict[str, object]],
        wiki_pages: list[dict[str, object]],
        total: int,
    ) -> None:
        self.entities = entities
        self.wiki_pages = wiki_pages
        self.total = total


@router.get("")
async def search_endpoint(
    q: str = Query(..., min_length=1),
    type: str = Query("all", pattern="^(all|entity|wiki)$"),
    novel_id: int | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
) -> dict[str, object]:
    entities: list[dict[str, object]] = []
    wiki_pages: list[dict[str, object]] = []

    if type in ("all", "entity"):
        entities = await search_entities(q, novel_id, limit)

    if type in ("all", "wiki"):
        wiki_pages = await search_wiki(q, novel_id, limit)

    return {
        "entities": entities,
        "wiki_pages": wiki_pages,
        "total": len(entities) + len(wiki_pages),
    }
