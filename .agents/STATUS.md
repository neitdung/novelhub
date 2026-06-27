# NovelHub Status

<!-- GENERATED: scripts/harness/render_status.py --write -->

- Current milestone: `foundation`
- Milestone accepted weight: 0/0 (100.0%)
- Backlog updated: `2026-06-27T15:50:13.259239Z`
- GitHub Project: https://github.com/neitdung/novelhub/projects

## Ready

None.

## In progress

| Task | State | Owner | Milestone | Dependencies |
|------|-------|-------|-----------|--------------|
| `NH-BEP-001` Backend Gaps for Import Preview, Factions, Wiki Lint/Backlinks, Chat Streaming, and Provider Health | `dev_complete` | developer | `parity` | none |

## Blocked / rework

None.

## Done

| Task | State | Owner | Milestone | Dependencies |
|------|-------|-------|-----------|--------------|
| `NH-CHAT-001` Chat CRUD and Messages API | `done` | unassigned | `unknown` | none |
| `NH-CHAT-002` Chat Tools: Wiki Search, Entity Lookup, Alias Resolution | `done` | unassigned | `unknown` | none |
| `NH-DISCOV-001` Knowledge Graph and Timeline API | `done` | unassigned | `unknown` | none |
| `NH-FE-001` WebSocket Analysis Progress | `done` | unassigned | `unknown` | none |
| `NH-FE-002` Theme System | `done` | unassigned | `unknown` | none |
| `NH-FE-003` Settings Page and Enhanced Navigation | `done` | unassigned | `unknown` | none |
| `NH-FOUND-001` Scaffold backend and frontend toolchains | `done` | unassigned | `unknown` | none |
| `NH-FOUND-003` SQLite migration baseline | `done` | unassigned | `unknown` | none |
| `NH-FOUND-005` OpenAPI contract and generated type check | `done` | unassigned | `unknown` | none |
| `NH-HARD-001` Security: sanitize_html, sanitize_url, sanitize_markdown, validate_input | `done` | unassigned | `unknown` | none |
| `NH-HARNESS-001` Bootstrap and validate the AI engineering harness | `done` | unassigned | `unknown` | none |
| `NH-HARNESS-002` Branch Naming, PR Creation, and PR-Based Review Workflow | `done` | unassigned | `unknown` | none |
| `NH-HARNESS-003` Stop tracking generated artifact .md files in .agents/ | `done` | unassigned | `unknown` | none |
| `NH-HARNESS-004` Fix GitHub CI: sync-pull artifact files, preserve metadata, add sync step | `done` | unassigned | `unknown` | none |
| `NH-INGEST-001` Novel upload API and storage | `done` | unassigned | `unknown` | none |
| `NH-INGEST-002` Chapter parsing and splitting | `done` | unassigned | `unknown` | none |
| `NH-INGEST-003` Unified External Source Ingestion and Chapter Handler | `done` | unassigned | `unknown` | none |
| `NH-INGEST-005` Frontend Source Management, Import Flow, and Chapter Handler UI | `done` | unassigned | `unknown` | none |
| `NH-KB-001` Entity Knowledge Base Schema and API | `done` | unassigned | `unknown` | none |
| `NH-KB-002` FTS5 Search | `done` | unassigned | `unknown` | none |
| `NH-KB-003` On-Demand Wiki Generation | `done` | unassigned | `unknown` | none |
| `NH-LLM-001` LLM provider interfaces | `done` | unassigned | `unknown` | none |
| `NH-LLM-002` Analysis pipeline | `done` | unassigned | `unknown` | none |
| `NH-NEXT-001` Refactor Frontend to Next.js (App Router, SPA Mode) | `done` | unassigned | `unknown` | none |
| `NH-NEXT-002` Sync Documents and Scripts After Next.js Refactor | `done` | unassigned | `unknown` | none |
| `NH-PORT-001` Export: Markdown Novel, JSON KB, Markdown Wiki | `done` | unassigned | `unknown` | none |
| `NH-PORT-002` Backup ZIP with Manifest/Checksum, Restore with Validation | `done` | unassigned | `unknown` | none |
| `NH-READ-001` Reader UI and navigation | `done` | unassigned | `unknown` | none |
| `NH-READ-002` Bookmarks and progress persistence | `done` | unassigned | `unknown` | none |
| `NH-TOOL-001` Clean Up Makefile and scripts/ Directory | `done` | unassigned | `unknown` | none |
| `NH-TOOL-002` Add Unified install Command | `done` | unassigned | `unknown` | none |
| `NH-TOOL-003` Add start, stop, clear Commands at Top of Makefile | `done` | unassigned | `unknown` | none |
| `NH-TOOL-004` Fix make install and make start Commands | `done` | unassigned | `unknown` | none |
| `NH-TOOL-005` Fix make start to Launch Frontend Dev Server | `done` | unassigned | `unknown` | none |

## Queued / proposed

| Task | State | Owner | Milestone | Dependencies |
|------|-------|-------|-----------|--------------|
| `NH-FEP-002` Bookshelf, Import, Source, and Chapter Management UI | `planning` | unassigned | `parity` | NH-FEP-001 |
| `NH-FEP-003` Analysis Dashboard with WebSocket Progress and Polling Fallback | `planning` | unassigned | `parity` | NH-FEP-001 |
| `NH-FEP-004` Reader UX with Bookmarks, Progress, Highlights, and Entity Drawer | `planning` | unassigned | `parity` | NH-FEP-001 |
| `NH-FEP-005` Entities, Wiki Browser, Search, Generation, and Backlink Workflows | `planning` | unassigned | `parity` | NH-FEP-001 |
| `NH-FEP-006` Graph, Shortest Path, Timeline, and Factions Visualization | `planning` | unassigned | `parity` | NH-FEP-001, NH-FEP-005 |
| `NH-FEP-007` Chat Conversations, Tool Execution, Citations, and Export | `planning` | unassigned | `parity` | NH-FEP-001 |
| `NH-FEP-008` Settings, Provider Health, Backup/Restore, and Export Workflows | `planning` | unassigned | `parity` | NH-FEP-001 |

## Active ownership

| Task | Branch | Owned paths |
|------|--------|-------------|
| `NH-BEP-001` | `feat/NH-BEP-001-backend-gaps` | `backend/app/routers/`<br>`backend/app/schemas.py`<br>`backend/app/crud.py` |

## Decisions and blockers

None recorded.

## Next valid action

Assign `NH-BEP-001` to QA and require a `<!-- qa-report -->` verdict.
