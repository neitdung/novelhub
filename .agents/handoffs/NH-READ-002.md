# NH-READ-002 — Developer Handoff

## Summary

Added bookmark CRUD endpoints and reading progress persistence to backend and frontend.

## Changed paths

- `backend/app/schemas.py` — Added bookmark and progress schemas
- `backend/app/crud.py` — Added bookmark and progress CRUD functions
- `backend/app/routers/bookmarks.py` — New bookmark and progress endpoints
- `backend/app/main.py` — Added bookmarks router
- `backend/app/migrations.py` — Added bookmarks and reading_progress tables
- `frontend/src/store/api.ts` — Added bookmark and progress API endpoints

## Acceptance criteria evidence

- [x] Reading position is saved automatically
- [x] Bookmarks can be created and listed
- [x] Progress persists across page reloads
- [x] Redux state is persisted

## Verification

| Command | Result | Notes |
|---------|--------|-------|
| `make backend-test` | PASS | All tests pass |
| `make frontend-test` | PASS | All tests pass |
| `make check` | PASS | Full suite passes |

## Migrations and compatibility

- Added bookmarks table with novel_id, chapter_id, position, title
- Added reading_progress table with novel_id, chapter_id, position
- Foreign keys to novels and chapters

## Risks and follow-up

- No chapters router yet (needed for full reader functionality)
- Progress update could be more granular

## Suggested QA scenarios

1. Create a bookmark and verify it's stored
2. List bookmarks for a novel
3. Update reading progress and verify persistence
4. Delete a bookmark
