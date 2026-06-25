# Developer Handoff: NH-DISCOV-001

## Summary
Implemented knowledge graph and timeline API for NovelHub.

## Files Changed
- backend/app/graph.py
- backend/app/timeline.py
- backend/app/routers/graph.py
- backend/tests/test_graph.py

## Implementation Details
- Graph: get_graph_data, shortest_path algorithms
- Timeline: Event CRUD, list_events with filtering
- API endpoints: /api/novels/{id}/graph, /api/novels/{id}/events

## Verification
- All tests pass: `cd backend && pytest tests/test_graph.py -v`
- Lint clean
- Type check clean
