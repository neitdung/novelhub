# NH-KB-003 Developer Handoff

## Summary
Implemented on-demand wiki generation with version tracking and source chapter references.

## Changes
- `backend/app/wiki/`: New module with generator and schemas
- `backend/app/routers/wiki.py`: Wiki API endpoints
- `backend/tests/test_wiki.py`: 7 tests covering wiki generation

## Verification
```bash
cd backend && .venv/bin/pytest tests/test_wiki.py -v
cd backend && .venv/bin/ruff check app/wiki/
cd backend && .venv/bin/mypy app/wiki/
```

## Notes
- Wiki generation uses FakeLLMProvider for testing
- Version tracking for wiki pages
- Source chapter references stored as JSON
