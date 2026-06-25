# NH-KB-002 Developer Handoff

## Summary
Implemented FTS5 full-text search with sync triggers for entities and wiki pages.

## Changes
- `backend/app/search.py`: FTS5 setup, rebuild, and search functions
- `backend/app/routers/search.py`: Search API endpoint
- `backend/tests/test_search.py`: 4 tests covering search functionality

## Verification
```bash
cd backend && .venv/bin/pytest tests/test_search.py -v
cd backend && .venv/bin/ruff check app/search.py
cd backend && .venv/bin/mypy app/search.py
```

## Notes
- FTS5 triggers keep index in sync with data
- Rebuild function for restoration scenarios
- Search supports filtering by novel_id
