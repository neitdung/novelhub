# NH-INGEST-003 Developer Handoff

## Summary

Implemented the unified external source ingestion and chapter handler feature. Provides configurable web scraping (69shuba via `scrapling`), source management CRUD, async import pipeline with progress tracking, and full chapter management (list, get, edit/correct, reimport, reparse, delete single/batch, swap).

## Changed files

| File | Change |
|------|--------|
| `backend/app/migrations.py` | Added migration v4: `sources`, `ingest_jobs` tables; extended `novels` (source_type, source_id) and `chapters` (raw_content, source_url, is_corrected, corrected_at, ingest_job_id) |
| `backend/app/schemas.py` | Added schemas: `SourceCreate/Update/Response/List`, `ImportRequest/Job/Status`, `ChapterResponse/List/Update`, `BatchChapterUpdate`, `BatchDeleteRequest`, `ChapterSwapRequest`, `TxtImportResponse` |
| `backend/app/crud.py` | Added CRUD: source operations (create/list/get/update/delete/count_novels), ingest job operations (create/update/get/list), chapter operations (create/list/get/update/delete_single/delete_range/delete_batch/swap/get_by_number/update_novel_source) |
| `backend/app/scraper.py` | New module: `BaseScraper` (retry, progress, range scraping), `ShubaScraper` (69shuba via StealthyFetcher, CSS extraction, Cloudflare bypass), `get_scraper()` factory |
| `backend/app/routers/sources.py` | New router: CRUD endpoints for sources + seed defaults |
| `backend/app/routers/chapters.py` | New router: chapter management (list, get, update, reimport, reparse, delete, batch-delete, batch-correct, swap) + import pipeline (start async import, poll status, list jobs) + txt import endpoint |
| `backend/app/main.py` | Registered `sources.router` and `chapters.router` |
| `backend/pyproject.toml` | Added `httpx`, `scrapling`, `python-multipart` dependencies |
| `backend/tests/test_ingestion.py` | 30 tests: source CRUD, chapter handler endpoints, scraper unit tests, txt import, import jobs, CRUD unit tests |

## Key implementation details

- **Scraper**: `ShubaScraper` uses `scrapling`'s `StealthyFetcher` with headless mode, Cloudflare bypass, CSS selector `.txtnav` extraction, exponential backoff retry. Falls back gracefully if scrapling not installed.
- **Import**: Async background task creates/updates chapters with raw_content stored separately. Progress tracked via `ingest_jobs` table.
- **Chapter handler**: Correction sets `is_corrected=1` and `corrected_at=CURRENT_TIMESTAMP`. Reimport re-fetches from source and updates raw_content (optionally resets content). Reparse re-runs chapter splitter on raw_content.
- **Migration**: Additive-only (ALTER TABLE ADD COLUMN). Existing data preserved with defaults.
- **Default source**: 69shuba seeded via `POST /api/sources/defaults`.

## Verification commands and results

```bash
# All 111 backend tests pass (30 new + 81 existing)
make backend-test
# Result: 111 passed in 41.55s

# Lint
make backend-lint
# Result: All checks passed!

# Typecheck
make backend-typecheck
# Result: Success: no issues found in 66 source files
```

## API endpoints added

### Sources
- `GET /api/sources/` — List sources
- `POST /api/sources/` — Create source
- `PUT /api/sources/{id}` — Update source
- `DELETE /api/sources/{id}` — Delete (only if no novels reference it)
- `POST /api/sources/defaults` — Seed default 69shuba source

### Import
- `POST /api/novels/{id}/import` — Start async import job
- `GET /api/novels/{id}/import/status/{job_id}` — Poll job progress
- `GET /api/novels/{id}/import/jobs` — List import jobs
- `POST /api/novels/import/txt` — Import from uploaded .txt/.md

### Chapters
- `GET /api/novels/{id}/chapters` — List chapters with metadata
- `GET /api/novels/{id}/chapters/{ch_id}` — Get full chapter
- `PUT /api/novels/{id}/chapters/{ch_id}` — Edit/correct chapter
- `POST /api/novels/{id}/chapters/{ch_id}/reimport` — Re-fetch from source
- `POST /api/novels/{id}/chapters/{ch_id}/reparse` — Re-run parser on raw
- `DELETE /api/novels/{id}/chapters/{ch_id}` — Delete single chapter
- `POST /api/novels/{id}/chapters/batch-delete` — Batch delete
- `POST /api/novels/{id}/chapters/batch-correct` — Batch correct
- `POST /api/novels/{id}/chapters/swap` — Swap chapter order

## Risks and blockers

- **scrapling dependency**: `ShubaScraper` requires `scrapling` package. If not installed, raises a clear error. The 69shuba-specific HTML structure (`.txtnav` div) may change and require selector updates.
- **Cloudflare**: 69shuba uses Cloudflare protection. `StealthyFetcher` in headless mode may not always bypass successfully on first attempt; retry logic mitigates this.
- **Async import**: Background task uses `asyncio.create_task`. In production with multiple workers, job state persistence handles recovery.
- **Migration compatibility**: ALTER TABLE ADD COLUMN is safe for existing SQLite databases.

## Recommended next step

Move to `dev_complete`. Next: implement NH-INGEST-005 (frontend UI for source management, import flow, and chapter handler).
