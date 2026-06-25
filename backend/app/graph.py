from __future__ import annotations

from .database import get_db_context


async def get_graph_data(
    novel_id: int,
    entity_type: str | None = None,
) -> dict[str, object]:
    async with get_db_context() as db:
        where = "WHERE novel_id = ?"
        params: list[object] = [novel_id]
        if entity_type:
            where += " AND entity_type = ?"
            params.append(entity_type)

        cursor = await db.execute(
            f"SELECT id, name, entity_type FROM entities {where}",
            params,
        )
        entities = [
            {"id": r[0], "name": r[1], "type": r[2]}
            for r in await cursor.fetchall()
        ]

        entity_ids = [e["id"] for e in entities]
        if not entity_ids:
            return {"nodes": entities, "edges": []}

        placeholders = ",".join("?" * len(entity_ids))
        cursor = await db.execute(
            f"SELECT source_entity_id, target_entity_id, relationship_type"
            f" FROM entity_relationships"
            f" WHERE novel_id = ? AND source_entity_id IN ({placeholders})"
            f" AND target_entity_id IN ({placeholders})",
            [novel_id, *entity_ids, *entity_ids],
        )
        edges = [
            {"source": r[0], "target": r[1], "type": r[2]}
            for r in await cursor.fetchall()
        ]

        return {"nodes": entities, "edges": edges}


async def shortest_path(
    novel_id: int,
    source_id: int,
    target_id: int,
    max_depth: int = 6,
) -> list[int] | None:
    async with get_db_context() as db:
        cursor = await db.execute(
            "SELECT source_entity_id, target_entity_id"
            " FROM entity_relationships WHERE novel_id = ?",
            (novel_id,),
        )
        edges = await cursor.fetchall()

        graph: dict[int, list[int]] = {}
        for src, tgt in edges:
            if src not in graph:
                graph[src] = []
            graph[src].append(tgt)
            if tgt not in graph:
                graph[tgt] = []
            graph[tgt].append(src)

        from collections import deque

        queue: deque[tuple[int, list[int]]] = deque([(source_id, [source_id])])
        visited = {source_id}

        while queue:
            node, path = queue.popleft()
            if node == target_id:
                return path
            if len(path) > max_depth:
                continue
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None
