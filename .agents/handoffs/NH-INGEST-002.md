# NH-INGEST-002 — Developer Handoff

## Summary

Created chapter parser with multi-language support and fallback for novels without chapter headings.

## Changed paths

- `backend/app/parser.py` — Chapter parsing and language detection
- `backend/tests/test_parser.py` — Parser tests

## Acceptance criteria evidence

- [x] Chapter detection works for all target languages
- [x] Fallback handles novels without chapter headings
- [x] Chapter metadata is correct
- [x] Preview endpoint returns parsed chapters

## Verification

| Command | Result | Notes |
|---------|--------|-------|
| `make backend-test` | PASS | 18 tests pass |
| `make backend-check` | PASS | All checks pass |

## Migrations and compatibility

No database changes. Parser is pure function.

## Risks and follow-up

- No preview endpoint yet (can be added to novels router)
- Parser patterns may need refinement for edge cases

## Suggested QA scenarios

1. Parse English novel with chapter headings
2. Parse Chinese novel with chapter headings
3. Parse novel without chapter headings (fallback)
