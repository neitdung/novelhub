# NH-INGEST-004 — Chapter Management and Correction API

## Metadata

- Milestone: `external-ingestion`
- Priority: P0
- Weight: 6
- Owner: unassigned
- Dependencies: `NH-INGEST-003`
- Proposed owned paths: `backend/app/routers/chapters.py`, `backend/app/crud.py`, `backend/app/schemas.py`
- ADRs: none

## Problem and outcome

After importing chapters, users need to view, correct, re-import, re-parse, and delete individual or batch chapters. Currently there is no chapter-level management API.

## In scope

- Chapter list/detail endpoints:
  - `GET /api/novels/{novel_id}/chapters` — List chapters with metadata (number, title, has_raw, has_content, created_at)
  - `GET /api/novels/{novel_id}/chapters/{chapter_id}` — Get full chapter content + raw_content
- Chapter correction:
  - `PUT /api/novels/{novel_id}/chapters/{chapter_id}` — Update chapter title, content, raw_content with version tracking
  - `PATCH /api/novels/{novel_id}/chapters/{chapter_id}/raw` — Update raw_content only (re-import fix)
- Chapter re-import:
  - `POST /api/novels/{novel_id}/chapters/{chapter_id}/reimport` — Re-fetch from source and replace raw_content
- Chapter re-parsing:
  - `POST /api/novels/{novel_id}/reparse` — Re-run parser on all (or range of) chapters from raw_content
- Chapter deletion:
  - `DELETE /api/novels/{novel_id}/chapters/{chapter_id}` — Delete single chapter
  - `DELETE /api/novels/{novel_id}/chapters` — Batch delete chapter range (body: chapter_start, chapter_end)
- Batch operations:
  - `POST /api/novels/{novel_id}/chapters/batch-correct` — Bulk update chapters (body: list of {chapter_id, title?, content?, raw_content?})
  - `POST /api/novels/{novel_id}/chapters/batch-delete` — Delete by list of chapter_ids
- Input validation and idempotency checks
- Tests for all endpoints

## Out of scope

- Frontend UI (separate task)
- LLM-based chapter correction
- Chapter reordering
- Diff/compare view between old and new content

## Acceptance criteria

- [ ] Chapter list/detail endpoints return correct data
- [ ] Chapter correction updates content and tracks changes
- [ ] Re-import re-fetches from source and updates raw_content
- [ ] Re-parsing regenerates chapter content from raw_content
- [ ] Single and batch delete work with proper cascade handling
- [ ] Batch correction updates multiple chapters atomically
- [ ] All endpoints validate input and return appropriate errors
- [ ] Tests pass for all endpoints

## Verification commands

```bash
make backend-test
make backend-lint
make backend-typecheck
```

## Documentation impact

Pending — API reference update needed for new chapter management endpoints.
