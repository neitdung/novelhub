# NH-FOUND-003 — Developer Handoff

## Summary

Added SQLite database connection management, WAL mode, foreign key enforcement, and a migration runner with schema version tracking.

## Changed paths

- `backend/app/database.py` — Database connection and health check
- `backend/app/migrations.py` — Migration runner with version tracking
- `backend/app/main.py` — Updated health endpoint to include database status
- `backend/tests/test_health.py` — Updated health tests
- `backend/tests/test_migrations.py` — New migration tests

## Acceptance criteria evidence

- [x] Database connects with WAL mode enabled
- [x] Foreign keys are enforced
- [x] Migration runner can apply and rollback migrations
- [x] Schema version is tracked in a metadata table
- [x] `/api/health` includes database status

## Verification

| Command | Result | Notes |
|---------|--------|-------|
| `make backend-check` | PASS | ruff, mypy, pytest all pass |
| `make check` | PASS | Full suite passes |

## Migrations and compatibility

- Initial migration creates `novels` and `chapters` tables
- Schema version tracked in `schema_version` table
- Migrations are idempotent

## Risks and follow-up

- No rollback migrations implemented yet (deferred)
- Database file path is hardcoded (config coming later)

## Suggested QA scenarios

1. Run `make backend-test` and verify all 6 tests pass
2. Verify `/api/health` returns `{"status": "ok", "database": "ok"}`
3. Verify migration is idempotent by running twice
