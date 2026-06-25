# NH-LLM-002 — Analysis pipeline

## Metadata

- Milestone: `analysis-pipeline`
- Priority: P0
- Weight: 5
- Owner: unassigned
- Dependencies: `NH-LLM-001`, `NH-INGEST-002`
- Proposed owned paths: `backend/`
- ADRs: none

## Problem and outcome

Create a resumable extraction pipeline that processes novels chapter by chapter with context management.

## In scope

- Chapter chunking with context budget
- Prompt versioning and templates
- Structured extraction for entity/fact types
- JSON extraction and normalization
- Processing queue with state transitions
- Crash recovery and resume
- Deterministic reduction and deduplication

## Out of scope

- Frontend integration
- Real-time updates
- Wiki generation

## Acceptance criteria

- [ ] Pipeline can process a chapter range
- [ ] Pipeline can pause, resume, and cancel
- [ ] Malformed output is handled gracefully
- [ ] Pipeline recovers after restart
- [ ] No duplicates on retry

## Verification commands

```bash
make backend-test
```

## Documentation impact

Pending.
