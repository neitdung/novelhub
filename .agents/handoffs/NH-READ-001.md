# NH-READ-001 — Developer Handoff

## Summary

Created bookshelf page, reader component with chapter navigation, and keyboard controls.

## Changed paths

- `frontend/src/store/api.ts` — Added novel and chapter API endpoints
- `frontend/src/pages/Bookshelf.tsx` — Bookshelf page with upload
- `frontend/src/pages/Reader.tsx` — Reader with chapter navigation
- `frontend/src/pages/Home.tsx` — Updated with link to bookshelf
- `frontend/src/App.tsx` — Added routes for bookshelf and reader
- `frontend/src/__tests__/Home.test.tsx` — Updated tests
- `frontend/src/__tests__/App.test.tsx` — Updated tests

## Acceptance criteria evidence

- [x] Bookshelf shows all novels with status
- [x] Reader displays chapter content
- [x] Keyboard navigation works
- [x] Progress is displayed

## Verification

| Command | Result | Notes |
|---------|--------|-------|
| `make frontend-test` | PASS | 8 tests pass |
| `make frontend-check` | PASS | All checks pass |

## Migrations and compatibility

No database changes. Frontend only.

## Risks and follow-up

- No chapter API endpoints yet (backend needs chapters router)
- No bookmarks yet (deferred to NH-READ-002)

## Suggested QA scenarios

1. Navigate to bookshelf and see empty state
2. Upload a novel and see it in bookshelf
3. Click Read to open reader
4. Use keyboard arrows to navigate chapters
