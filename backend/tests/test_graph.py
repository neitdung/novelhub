from __future__ import annotations

import pytest

from app.database import get_db_context
from app.graph import get_graph_data, shortest_path
from app.timeline import EventCreate, create_event, list_events


async def _create_novel(novel_id: int = 1) -> None:
    async with get_db_context() as db:
        await db.execute(
            "INSERT INTO novels (id, title, author, file_path, file_hash)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                novel_id,
                f"Test Novel {novel_id}",
                "Author",
                f"/tmp/{novel_id}.txt",
                f"hash{novel_id}",
            ),
        )
        await db.commit()


@pytest.mark.asyncio
async def test_get_graph_data() -> None:
    await _create_novel(1)
    graph = await get_graph_data(novel_id=1)
    assert "nodes" in graph
    assert "edges" in graph
    assert isinstance(graph["nodes"], list)


@pytest.mark.asyncio
async def test_shortest_path() -> None:
    await _create_novel(1)
    path = await shortest_path(novel_id=1, source_id=1, target_id=2)
    assert path is None or isinstance(path, list)


@pytest.mark.asyncio
async def test_create_event() -> None:
    await _create_novel(1)
    data = EventCreate(
        novel_id=1,
        event_type="battle",
        title="The Great Battle",
        description="A massive battle",
        importance=5,
    )
    event = await create_event(data)
    assert event.title == "The Great Battle"
    assert event.importance == 5


@pytest.mark.asyncio
async def test_list_events() -> None:
    await _create_novel(1)
    await create_event(
        EventCreate(novel_id=1, title="Event 1", event_type="general")
    )
    await create_event(
        EventCreate(novel_id=1, title="Event 2", event_type="battle")
    )
    events, total = await list_events(novel_id=1)
    assert total == 2
    assert len(events) == 2


@pytest.mark.asyncio
async def test_list_events_by_type() -> None:
    await _create_novel(1)
    await create_event(
        EventCreate(novel_id=1, title="Event 1", event_type="general")
    )
    await create_event(
        EventCreate(novel_id=1, title="Event 2", event_type="battle")
    )
    events, total = await list_events(novel_id=1, event_type="battle")
    assert total == 1
    assert events[0].event_type == "battle"
