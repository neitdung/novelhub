# NH-KB-003 — On-Demand Wiki Generation

## Objective
Generate wiki pages on demand from entity KB, with source chapter references and versioning.

## Acceptance Criteria
1. Wiki generation API: `POST /api/wiki/generate` with novel_id, entity_id, language
2. Wiki stored with version tracking, source chapter references
3. Wiki CRUD: get, list, delete, regenerate
4. Backlinks between related entities
5. Tests using FakeLLMProvider

## Verification
```bash
cd backend && .venv/bin/pytest tests/test_wiki.py -v
```

## Owned Paths
- `backend/app/wiki/` (new module)
- `backend/app/routers/wiki.py` (new router)
- `backend/tests/test_wiki.py` (new test file)
