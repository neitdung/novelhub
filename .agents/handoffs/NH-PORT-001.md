# Developer Handoff: NH-PORT-001

## Summary
Implemented export: Markdown novel, JSON KB, Markdown wiki.

## Files Changed
- backend/app/export.py
- backend/app/routers/export.py
- backend/tests/test_export.py

## Implementation Details
- export_novel_markdown: Full novel with chapters
- export_novel_json: Novel data with chapters
- export_wiki_markdown: Published wiki pages
- API endpoints: /api/novels/{id}/export/*

## Verification
- All tests pass: `cd backend && pytest tests/test_export.py -v`
- Lint clean
- Type check clean
