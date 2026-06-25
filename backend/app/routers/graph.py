from __future__ import annotations

from fastapi import APIRouter, Query

from ..graph import get_graph_data, shortest_path
from ..timeline import EventCreate, EventList, EventResponse, create_event, list_events

router = APIRouter(prefix="/api", tags=["discovery"])


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
