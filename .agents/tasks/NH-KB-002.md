# NH-KB-002 — FTS5 Search

## Objective
Add FTS5 full-text search indexes for entities and wiki pages with sync triggers.

## Acceptance Criteria
1. FTS5 virtual tables for entities (name, type, aliases) and wiki pages (title, content)
2. Triggers to sync FTS on insert/update/delete
3. Search API: `GET /api/search?q=...&type=entity|wiki`
4. Unicode-aware tokenization for EN/ZH/VI
5. Tests for search ranking, rebuild, and restore scenarios

## Verification
```bash
cd backend && .venv/bin/pytest tests/test_search.py -v
```

## Owned Paths
- `backend/app/search.py` (new module)
- `backend/app/routers/search.py` (new router)
- `backend/tests/test_search.py` (new test file)
