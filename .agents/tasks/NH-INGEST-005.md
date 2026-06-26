# NH-INGEST-005 — Frontend Source Management, Import Flow, and Chapter Handler UI

## Metadata

- Milestone: `external-ingestion`
- Priority: P1
- Weight: 7
- Owner: unassigned
- Dependencies: `NH-INGEST-003`
- Proposed owned paths: `frontend/src/pages/Sources.tsx`, `frontend/src/pages/ChapterManager.tsx`, `frontend/src/store/api.ts`, `frontend/src/App.tsx`, `frontend/src/components/`
- ADRs: none

## Problem and outcome

Users need a complete UI to manage external sources, trigger imports with progress, and handle chapters end-to-end — view, correct, re-import, re-parse, and delete chapters.

## In scope

### Sources Page (`/sources`)
- List all configured sources in a table (name, language, active status)
- "Add Source" form/button with fields: name, url_template, css_selector, language
- Per-source edit button (inline or modal form)
- Per-source delete with confirmation
- "Seed defaults" button to add built-in sources (69shuba)
- Source card shows: name, language badge, active toggle, URL template preview

### Import Flow (on Sources page or Reader page)
- For each source, an "Import" action:
  - Select target novel from dropdown (or create new novel inline)
  - Enter chapter range (start, end)
  - Show import progress bar with status updates (polled from backend)
  - On completion: show summary (X chapters imported, Y failed)
  - Error display for failed chapters
- Import jobs history list per novel

### Chapter Manager Page (`/novel/:novelId/chapters`)
- Full chapter list table:
  - Columns: #, Title, Has Raw (icon), Has Content (icon), Corrected (icon), Created, Actions
  - Sortable by chapter number
  - Pagination
- Per-chapter actions:
  - "View/Edit" — expandable inline editor for title, content, raw_content
  - "Reimport" button with confirmation (optionally reset content)
  - "Reparse" button
  - "Delete" with confirmation dialog
- Batch actions:
  - Checkbox selection per row
  - "Batch Delete" (selected range)
  - "Batch Reimport"
- Correction indicator shows edit history (corrected badge + timestamp)

### API Service Updates (`frontend/src/store/api.ts`)
- Sources endpoints: getSources, createSource, updateSource, deleteSource, seedDefaults
- Import endpoints: startImport (returns job_id), getImportStatus, getImportJobs
- Chapter management endpoints: getChapters, getChapter, updateChapter, reimportChapter, reparseChapter, deleteChapter, batchDeleteChapters, batchUpdateChapters
- New TypeScript interfaces: Source, ImportJob, ChapterDetail

### Routing & Navigation
- `/sources` route → Sources page
- `/novel/:novelId/chapters` route → Chapter Manager page
- Add "Sources" link to Layout navigation
- Add "Manage Chapters" link on Reader page / Bookshelf novel cards

### UI States
- Loading, empty, error states for all pages (following existing patterns in EmptyState/LoadingState/ErrorState)
- Confirmation dialogs for destructive actions
- Toast notifications for success/error feedback

## Out of scope

- Dark/light theme customization (follow existing Chakra UI theme)
- Drag-and-drop chapter reordering
- Real-time WebSocket import progress (polling is fine for v1)

## Acceptance criteria

- [ ] Sources page lists, creates, edits, and deletes sources
- [ ] Import flow creates import job and shows progress
- [ ] Chapter list displays all metadata with status icons
- [ ] Chapter editor can correct content (shows is_corrected flag after save)
- [ ] Reimport button triggers re-fetch and updates display
- [ ] Reparse button regenerates content from raw
- [ ] Delete works with confirmation for single and batch
- [ ] Batch selection and operations work
- [ ] Navigation includes Sources and Chapter Manager links
- [ ] All UI states (loading, empty, error) render correctly
- [ ] Frontend tests pass

## Verification commands

```bash
make frontend-test
make frontend-lint
make frontend-typecheck
```

## Documentation impact

Pending.
