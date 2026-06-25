# NH-DISCOV-001 — Knowledge Graph and Timeline

## Objective
Implement knowledge graph and timeline visualization APIs.

## Acceptance Criteria
1. Graph API: entities, relationships, shortest path
2. Timeline API: events, chapters, participants
3. Graph filtering by entity type
4. Tests for graph and timeline queries

## Verification
```bash
cd backend && .venv/bin/pytest tests/test_graph.py -v
```

## Owned Paths
- `backend/app/graph.py` (new module)
- `backend/app/timeline.py` (new module)
- `backend/app/routers/graph.py` (new router)
