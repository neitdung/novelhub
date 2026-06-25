# NH-KB-001 — Entity Knowledge Base Schema and API

## Objective
Extend the database schema with entity profiles, aliases, mentions, relationships, and implement CRUD API.

## Acceptance Criteria
1. New migration adds tables: `entities`, `entity_aliases`, `entity_mentions`, `entity_relationships`
2. Entity CRUD API: list (with type filter), get, create, update, delete
3. Alias resolution: normalized exact matching, merge support
4. All tests pass, lint clean

## Verification
```bash
cd backend && .venv/bin/pytest tests/test_kb.py -v
cd backend && .venv/bin/ruff check app/
cd backend && .venv/bin/mypy app/
```

## Owned Paths
- `backend/app/migrations.py` (add migration v2)
- `backend/app/kb/` (new module)
- `backend/app/routers/kb.py` (new router)
- `backend/app/schemas.py` (add KB schemas)
- `backend/tests/test_kb.py` (new test file)
