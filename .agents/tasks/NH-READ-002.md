# NH-READ-002 — Bookmarks and progress persistence

## Metadata

- Milestone: `ingestion-reader`
- Priority: P0
- Weight: 3
- Owner: unassigned
- Dependencies: `NH-READ-001`
- Proposed owned paths: `backend/`, `frontend/`
- ADRs: none

## Problem and outcome

Persist reading progress and bookmarks across sessions.

## In scope

- Reading progress tracking per novel
- Bookmark creation and management
- Progress sync between backend and frontend
- Redux state persistence

## Out of scope

- Multiple reading positions
- Export/import bookmarks

## Acceptance criteria

- [ ] Reading position is saved automatically
- [ ] Bookmarks can be created and listed
- [ ] Progress persists across page reloads
- [ ] Redux state is persisted

## Verification commands

```bash
make check
```

## Documentation impact

Pending.
