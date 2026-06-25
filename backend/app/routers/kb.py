from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ..database import get_db_context
from ..kb.crud import (
    create_entity,
    delete_entity,
    get_entity,
    list_entities,
    merge_entities,
    resolve_alias,
    update_entity,
)
from ..kb.schemas import (
    EntityCreate,
    EntityList,
    EntityResponse,
    EntityUpdate,
    MentionCreate,
    MergeRequest,
)

router = APIRouter(prefix="/api/kb", tags=["knowledge-base"])


@router.get("/entities", response_model=EntityList)
async def list_entities_endpoint(
    novel_id: int,
    entity_type: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> EntityList:
    entities, total = await list_entities(novel_id, entity_type, limit, offset)
    return EntityList(entities=entities, total=total)


@router.get("/entities/{entity_id}", response_model=EntityResponse)
async def get_entity_endpoint(entity_id: int) -> EntityResponse:
    entity = await get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.post("/entities", response_model=EntityResponse, status_code=201)
async def create_entity_endpoint(data: EntityCreate) -> EntityResponse:
    return await create_entity(data)


@router.patch("/entities/{entity_id}", response_model=EntityResponse)
async def update_entity_endpoint(
    entity_id: int, data: EntityUpdate
) -> EntityResponse:
    entity = await update_entity(entity_id, data)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.delete("/entities/{entity_id}")
async def delete_entity_endpoint(entity_id: int) -> dict[str, str]:
    deleted = await delete_entity(entity_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entity not found")
    return {"status": "deleted"}


@router.post("/resolve", response_model=EntityResponse | None)
async def resolve_alias_endpoint(
    name: str, novel_id: int
) -> EntityResponse | None:
    entity_id = await resolve_alias(name, novel_id)
    if not entity_id:
        return None
    return await get_entity(entity_id)


@router.post("/merge", response_model=EntityResponse)
async def merge_entities_endpoint(data: MergeRequest) -> EntityResponse:
    async with get_db_context() as db:
        source = await get_entity(data.source_entity_id, db)
        if not source:
            raise HTTPException(
                status_code=404, detail="Source entity not found"
            )
        result = await merge_entities(data, source.novel_id, db)
        if not result:
            raise HTTPException(
                status_code=400, detail="Merge failed"
            )
        return result


@router.post("/entities/{entity_id}/mentions")
async def add_mention_endpoint(
    entity_id: int, data: MentionCreate
) -> dict[str, str]:
    async with get_db_context() as db:
        entity = await get_entity(entity_id, db)
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        await db.execute(
            "INSERT INTO entity_mentions"
            " (entity_id, chapter_id, position, context)"
            " VALUES (?, ?, ?, ?)",
            (entity_id, data.chapter_id, data.position, data.context),
        )
        await db.commit()
        return {"status": "added"}
