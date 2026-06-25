# NH-PORT-001 — Export API

## Objective
Implement export to Markdown and JSON formats.

## Acceptance Criteria
1. Export novel as Markdown with chapters
2. Export knowledge base as JSON
3. Export wiki pages as Markdown
4. Tests for all export formats

## Verification
```bash
cd backend && .venv/bin/pytest tests/test_export.py -v
```

## Owned Paths
- `backend/app/export.py` (new module)
- `backend/app/routers/export.py` (new router)
