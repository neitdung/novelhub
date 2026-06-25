from __future__ import annotations

import json

from pydantic import BaseModel

from .database import get_db_context


class EventCreate(BaseModel):
    novel_id: int
    chapter_id: int | None = None
    event_type: str = "general"
    title: str = ""
    description: str = ""
    importance: int = 1
    participants: list[int] = []
    attributes: dict[str, object] = {}


class EventResponse(BaseModel):
    id: int
    novel_id: int
    chapter_id: int | None
    event_type: str
    title: str
    description: str
    importance: int
    participants: list[int]
    attributes: dict[str, object]
    created_at: str


class EventList(BaseModel):
    events: list[EventResponse]
    total: int


def parse_participants(raw: str | None) -> list[int]:
    if not raw:
        return []
    try:
        result = json.loads(raw)
        if isinstance(result, list):
            return result
    except (json.JSONDecodeError, TypeError):
        pass
    return []


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


async def create_event(data: EventCreate) -> EventResponse:
    async with get_db_context() as db:
        participants_json = json.dumps(data.participants)
        attributes_json = json.dumps(data.attributes, ensure_ascii=False)

        cursor = await db.execute(
            "INSERT INTO events"
            " (novel_id, chapter_id, event_type, title, description,"
            " importance, participants, attributes)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                data.novel_id,
                data.chapter_id,
                data.event_type,
                data.title,
                data.description,
                data.importance,
                participants_json,
                attributes_json,
            ),
        )
        event_id = cursor.lastrowid
        assert event_id is not None
        await db.commit()

        return EventResponse(
            id=event_id,
            novel_id=data.novel_id,
            chapter_id=data.chapter_id,
            event_type=data.event_type,
            title=data.title,
            description=data.description,
            importance=data.importance,
            participants=data.participants,
            attributes=data.attributes,
            created_at="",
        )


async def list_events(
    novel_id: int,
    event_type: str | None = None,
    chapter_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[EventResponse], int]:
    async with get_db_context() as db:
        where = "WHERE novel_id = ?"
        params: list[object] = [novel_id]
        if event_type:
            where += " AND event_type = ?"
            params.append(event_type)
        if chapter_id:
            where += " AND chapter_id = ?"
            params.append(chapter_id)

        count_cursor = await db.execute(
            f"SELECT COUNT(*) FROM events {where}", params
        )
        count_row = await count_cursor.fetchone()
        total = count_row[0] if count_row else 0

        cursor = await db.execute(
            f"SELECT id, novel_id, chapter_id, event_type, title,"
            f" description, importance, participants, attributes,"
            f" created_at FROM events {where}"
            f" ORDER BY chapter_id ASC, importance DESC"
            f" LIMIT ? OFFSET ?",
            [*params, limit, offset],
        )
        rows = await cursor.fetchall()

        events = [
            EventResponse(
                id=r[0],
                novel_id=r[1],
                chapter_id=r[2],
                event_type=r[3],
                title=r[4],
                description=r[5],
                importance=r[6],
                participants=parse_participants(r[7]),
                attributes=parse_attributes(r[8]),
                created_at=str(r[9]),
            )
            for r in rows
        ]

        return events, total
