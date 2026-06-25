# NH-READ-001 — Reader UI and navigation

## Metadata

- Milestone: `ingestion-reader`
- Priority: P0
- Weight: 4
- Owner: unassigned
- Dependencies: `NH-INGEST-002`, `NH-FOUND-001`
- Proposed owned paths: `frontend/`
- ADRs: none

## Problem and outcome

Create a bookshelf page and reader component for reading novels with navigation and keyboard controls.

## In scope

- Bookshelf page listing all novels
- Reader component with chapter navigation
- Keyboard navigation (arrow keys, page up/down)
- Reading progress display
- Responsive layout

## Out of scope

- Bookmarks (NH-READ-002)
- Reader preferences
- Search

## Acceptance criteria

- [ ] Bookshelf shows all novels with status
- [ ] Reader displays chapter content
- [ ] Keyboard navigation works
- [ ] Progress is displayed

## Verification commands

```bash
make frontend-test
```

## Documentation impact

Pending.
