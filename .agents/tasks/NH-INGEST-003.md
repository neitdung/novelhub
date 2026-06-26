# NH-INGEST-003 — Unified External Source Ingestion and Chapter Handler

## Metadata

- Milestone: `external-ingestion`
- Priority: P0
- Weight: 13
- Owner: unassigned
- Dependencies: `NH-FOUND-003`
- Proposed owned paths: `backend/app/scraper.py`, `backend/app/routers/sources.py`, `backend/app/routers/chapters.py`, `backend/app/crud.py`, `backend/app/schemas.py`, `backend/app/migrations.py`, `backend/pyproject.toml`
- ADRs: none

## Problem and outcome

NovelHub needs a complete ingest-to-handle pipeline: import chapters from external sources (like 69shuba) or from uploaded files, store raw text in the DB, then provide a full chapter handler that can list, correct, re-import, re-parse, and delete chapters — including editing old/existing data. The entire flow from ingestion through chapter management must be seamless.

## In scope

### Database (Migration v4)
- New `sources` table: id, name, url_template, novel_id_pattern, chapter_id_pattern, css_selector, language, active, created_at, updated_at
- New `ingest_jobs` table: id, novel_id, source_id, chapter_start, chapter_end, status (pending/running/completed/failed), progress, error, created_at, updated_at
- Add to `chapters` table: `raw_content TEXT`, `source_url TEXT`, `is_corrected INTEGER DEFAULT 0`, `corrected_at TIMESTAMP`, `ingest_job_id INTEGER REFERENCES ingest_jobs(id)`
- Add to `novels` table: `source_type TEXT DEFAULT 'upload'` (upload, scrape), `source_id INTEGER REFERENCES sources(id)`

### Scraper module (`backend/app/scraper.py`)
- `BaseScraper` abstract class with interface: `fetch_chapter(chapter_number) -> str`
- `ShubaScraper` implementation for 69shuba.com:
  - Uses `scrapling` `StealthyFetcher` with Cloudflare bypass
  - CSS selector-based content extraction (`.txtnav`)
  - Retry with exponential backoff (configurable max_retries, delay)
  - Progress callbacks
- Configurable per source via `url_template`, CSS selector, language
- Support for headless and network-idle options

### Source Management API (`/api/sources`)
- `GET /api/sources` — List all configured sources
- `POST /api/sources` — Create source (name, url_template, css_selector, language, active)
- `PUT /api/sources/{id}` — Update source config
- `DELETE /api/sources/{id}` — Delete source (only if no active novels reference it)
- `POST /api/sources/defaults` — Seed default sources (69shuba)

### Import Pipeline (`/api/novels/{novel_id}/import`)
- `POST /api/novels/{novel_id}/import` — Start import job:
  - Body: source_id, chapter_start, chapter_end, (optional) url_template_params
  - Creates `ingest_jobs` record with pending status
  - Launches background asyncio task
  - Returns job_id immediately
  - On completion: chapters saved to DB with raw_content + source_url
- `GET /api/novels/{novel_id}/import/status` — Poll import progress
- `GET /api/novels/{novel_id}/import/jobs` — List past import jobs
- `POST /api/import/txt` — Import from uploaded .txt/.md file:
  - Parses file, creates novel, stores raw chapters
  - Reuses existing upload flow + enhancement

### Chapter Handler API (`/api/novels/{novel_id}/chapters`)
- `GET /api/novels/{novel_id}/chapters` — List chapters (id, number, title, has_raw, has_content, is_corrected, created_at)
- `GET /api/novels/{novel_id}/chapters/{chapter_id}` — Full chapter (title, content, raw_content, source_url, metadata)
- `PUT /api/novels/{novel_id}/chapters/{chapter_id}` — Edit/correct chapter: update title, content, raw_content. Sets `is_corrected=1`, `corrected_at=now`
- `POST /api/novels/{novel_id}/chapters/{chapter_id}/reimport` — Re-fetch from source, replace raw_content. Optionally also reset content if `reset_content=true`
- `POST /api/novels/{novel_id}/chapters/{chapter_id}/reparse` — Re-run chapter parser on raw_content to regenerate content
- `DELETE /api/novels/{novel_id}/chapters/{chapter_id}` — Delete single chapter
- `DELETE /api/novels/{novel_id}/chapters` — Batch delete (body: chapter_ids list or chapter_start/chapter_end range)
- `POST /api/novels/{novel_id}/chapters/batch` — Batch operations: correct, reimport, delete multiple chapters at once
- `PUT /api/novels/{novel_id}/chapters/swap` — Swap chapter order (chapter_id_a, chapter_id_b)

### Default source seeding
- On first migration/startup, seed a 69shuba source:
  - name: "69shuba"
  - url_template: `https://www.69shuba.com/txt/{novel_id}/{chapter_id}`
  - css_selector: `.txtnav`
  - language: "zh"

### Dependencies
- Add `scrapling>=0.1.0` to pyproject.toml

### Tests
- Scraper tests (mock HTTP, test extraction, test retry logic)
- Source CRUD tests
- Import job lifecycle tests
- Chapter handler endpoint tests (list, get, edit, reimport, reparse, delete, batch)
- Migration tests

## Out of scope

- Frontend UI (separate task NH-INGEST-FE-001)
- Translation pipeline
- LLM-based content processing
- Multiple simultaneous imports for same novel

## Acceptance criteria

- [ ] Migration v4 runs cleanly with all new tables/columns
- [ ] Sources CRUD works with validation
- [ ] Scraper module can fetch and extract text from 69shuba
- [ ] Import endpoint creates ingest job, runs async, stores raw chapters
- [ ] Import progress can be polled
- [ ] Chapter list shows metadata correctly
- [ ] Chapter correction sets is_corrected flag and timestamp
- [ ] Re-import re-fetches from source and updates raw_content
- [ ] Re-parse regenerates content from raw_content
- [ ] Single and batch delete work with cascade
- [ ] Batch operations work atomically
- [ ] Old/existing data can be edited, reimported, and corrected
- [ ] .txt file import stores raw chapters
- [ ] All tests pass

## Verification commands

```bash
make backend-test
make backend-lint
make backend-typecheck
```

## Documentation impact

Pending.
