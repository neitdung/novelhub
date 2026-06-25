# NH-INGEST-002 — Chapter parsing and splitting

## Metadata

- Milestone: `ingestion-reader`
- Priority: P0
- Weight: 4
- Owner: unassigned
- Dependencies: `NH-INGEST-001`
- Proposed owned paths: `backend/`
- ADRs: none

## Problem and outcome

Parse uploaded novels into chapters using configurable patterns with safe fallback for novels without chapter headings.

## In scope

- Chapter detection with configurable patterns
- Support for Chinese, Vietnamese, and English chapter headings
- Safe fallback for novels without chapters
- Chapter metadata (number, title, content)
- Preview before commit

## Out of scope

- LLM-based chapter detection
- Frontend UI
- Chapter editing

## Acceptance criteria

- [ ] Chapter detection works for all target languages
- [ ] Fallback handles novels without chapter headings
- [ ] Chapter metadata is correct
- [ ] Preview endpoint returns parsed chapters

## Verification commands

```bash
make backend-test
```

## Documentation impact

Pending.
