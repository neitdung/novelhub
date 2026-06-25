# NH-INGEST-001 — Developer Handoff

## Summary

Created novel upload API with file validation, duplicate detection, and CRUD operations.

## Changed paths

- `backend/app/schemas.py` — Novel request/response models
- `backend/app/crud.py` — Database CRUD operations
- `backend/app/routers/novels.py` — Upload and list endpoints
- `backend/app/main.py` — Added router
- `backend/app/migrations.py` — Updated novels table schema
- `backend/tests/test_novels.py` — Novel API tests
- `backend/tests/conftest.py` — Test database setup

## Acceptance criteria evidence

- [x] Upload endpoint accepts .txt and .md files
- [x] File size and encoding validation works
- [x] Duplicate files are detected by hash
- [x] Novel metadata is extracted and stored
- [x] CRUD operations work for novels

## Verification

| Command | Result | Notes |
|---------|--------|-------|
| `make backend-check` | PASS | 11 tests pass |

## Migrations and compatibility

- Updated novels table with author, file_path, file_hash columns
- Migrations are idempotent

## Risks and follow-up

- No file content parsing yet (deferred to NH-INGEST-002)
- No delete endpoint yet

## Suggested QA scenarios

1. Upload a .txt file and verify metadata
2. Try uploading duplicate file and verify rejection
3. List novels and verify results
