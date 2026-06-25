# NH-INGEST-001 — Novel upload API and storage

## Metadata

- Milestone: `ingestion-reader`
- Priority: P0
- Weight: 5
- Owner: unassigned
- Dependencies: `NH-FOUND-003`
- Proposed owned paths: `backend/`
- ADRs: none

## Problem and outcome

Create API endpoints for uploading novel files (.txt, .md) with validation, storage, and metadata extraction.

## In scope

- File upload endpoint with size/encoding validation
- Duplicate detection via file hash
- Novel metadata extraction (title, author, language)
- Novel CRUD operations
- File storage in local directory

## Out of scope

- Chapter parsing (NH-INGEST-002)
- LLM analysis
- Frontend UI

## Acceptance criteria

- [ ] Upload endpoint accepts .txt and .md files
- [ ] File size and encoding validation works
- [ ] Duplicate files are detected by hash
- [ ] Novel metadata is extracted and stored
- [ ] CRUD operations work for novels

## Verification commands

```bash
make backend-test
```

## Documentation impact

Pending.
