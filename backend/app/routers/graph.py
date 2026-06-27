from __future__ import annotations

from fastapi import APIRouter, Query

from ..database import get_db_context
from ..graph import get_graph_data, shortest_path
from ..kb.crud import list_entities
from ..schemas import FactionEntity, FactionList, FactionRelationship, FactionResponse
from ..timeline import EventCreate, EventList, EventResponse, create_event, list_events

router = APIRouter(prefix="/api", tags=["discovery"])


@router.get("/graph/{novel_id}/factions", response_model=FactionList)
async def get_factions_endpoint(novel_id: int) -> FactionList:
    """Return organization entities and their relationships as a faction projection."""
    entities, _ = await list_entities(novel_id, entity_type="organization", limit=200)

    factions: list[FactionResponse] = []
    for entity in entities:
        async with get_db_context() as db:
            cursor = await db.execute(
                "SELECT source_entity_id, target_entity_id, relationship_type"
                " FROM entity_relationships"
                " WHERE novel_id = ?"
                " AND (source_entity_id = ? OR target_entity_id = ?)",
                (novel_id, entity.id, entity.id),
            )
            rows = await cursor.fetchall()

        relationships = [
            FactionRelationship(
                source_entity_id=r[0],
                target_entity_id=r[1],
                relationship_type=r[2],
            )
            for r in rows
        ]

        factions.append(
            FactionResponse(
                entity=FactionEntity(
                    id=entity.id,
                    name=entity.name,
                    entity_type=entity.entity_type,
                    aliases=entity.aliases,
                ),
                relationships=relationships,
            )
        )

    return FactionList(factions=factions, total=len(factions))


@router.get("/graph/{novel_id}")
async def get_graph_endpoint(
    novel_id: int,
    entity_type: str | None = Query(None),
) -> dict[str, object]:
    return await get_graph_data(novel_id, entity_type)


@router.get("/graph/{novel_id}/path")
async def shortest_path_endpoint(
    novel_id: int,
    source_id: int,
    target_id: int,
) -> dict[str, object]:
    path = await shortest_path(novel_id, source_id, target_id)
    return {"path": path, "found": path is not None}


@router.post("/events", response_model=EventResponse, status_code=201)
async def create_event_endpoint(data: EventCreate) -> EventResponse:
    return await create_event(data)


@router.get("/events/{novel_id}", response_model=EventList)
async def list_events_endpoint(
    novel_id: int,
    event_type: str | None = Query(None),
    chapter_id: int | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> EventList:
    events, total = await list_events(
        novel_id, event_type, chapter_id, limit, offset
    )
    return EventList(events=events, total=total)
