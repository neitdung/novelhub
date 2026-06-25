# NH-FOUND-003 — SQLite migration baseline

## Metadata

- Milestone: `foundation`
- Priority: P0
- Weight: 2
- Owner: unassigned
- Dependencies: `NH-FOUND-001`
- Proposed owned paths: `backend/`
- ADRs: none

## Problem and outcome

Establish SQLite database connection management, WAL mode, foreign keys, and a migration runner that can apply schema changes incrementally.

## In scope

- SQLite connection management with aiosqlite
- WAL mode and foreign key enforcement
- Migration runner (alembic or custom)
- Initial schema version tracking
- Database health check endpoint

## Out of scope

- Feature tables (novels, chapters, entities)
- FTS5 configuration
- Data import/export

## Acceptance criteria

- [ ] Database connects with WAL mode enabled
- [ ] Foreign keys are enforced
- [ ] Migration runner can apply and rollback migrations
- [ ] Schema version is tracked in a metadata table
- [ ] `/api/health` includes database status

## Verification commands

```bash
make backend-test
```

## Documentation impact

Pending.
