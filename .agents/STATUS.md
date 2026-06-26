# NovelHub Status

<!-- GENERATED: scripts/harness/render_status.py --write -->

- Current milestone: `external-ingestion`
- Milestone accepted weight: 0/20 (0.0%)
- Backlog updated: `2026-06-26T07:18:07Z`

## Ready

None.

## In progress

| Task | State | Owner | Milestone | Dependencies |
|------|-------|-------|-----------|--------------|
| `NH-INGEST-003` Unified External Source Ingestion and Chapter Handler | `dev_complete` | developer-ingest-003 | `external-ingestion` | NH-FOUND-003 |

## Blocked / rework

None.

## Done

| Task | State | Owner | Milestone | Dependencies |
|------|-------|-------|-----------|--------------|
| `NH-CHAT-001` Chat CRUD and Messages API | `done` | developer-chat-001 | `discovery-chat` | NH-KB-001 |
| `NH-CHAT-002` Chat Tools: Wiki Search, Entity Lookup, Alias Resolution | `done` | developer-chat-002 | `discovery-chat` | NH-CHAT-001, NH-KB-002 |
| `NH-DISCOV-001` Knowledge Graph and Timeline API | `done` | developer-discov-001 | `discovery-chat` | NH-KB-001 |
| `NH-FE-001` WebSocket Analysis Progress | `done` | developer-fe-001 | `core-frontend` | NH-LLM-002 |
| `NH-FE-002` Theme System | `done` | developer-fe-002 | `core-frontend` | none |
| `NH-FE-003` Settings Page and Enhanced Navigation | `done` | developer-fe-003 | `core-frontend` | none |
| `NH-FOUND-001` Scaffold backend and frontend toolchains | `done` | developer-found-001 | `foundation` | NH-HARNESS-001 |
| `NH-FOUND-003` SQLite migration baseline | `done` | developer-found-003 | `foundation` | NH-FOUND-001 |
| `NH-FOUND-005` OpenAPI contract and generated type check | `done` | developer-found-005 | `foundation` | NH-FOUND-001 |
| `NH-HARD-001` Security: sanitize_html, sanitize_url, sanitize_markdown, validate_input | `done` | developer-hard-001 | `hardening-release` | none |
| `NH-HARNESS-001` Bootstrap and validate the AI engineering harness | `done` | developer-bootstrap | `harness-bootstrap` | none |
| `NH-INGEST-001` Novel upload API and storage | `done` | developer-ingest-001 | `ingestion-reader` | NH-FOUND-003 |
| `NH-INGEST-002` Chapter parsing and splitting | `done` | developer-ingest-002 | `ingestion-reader` | NH-INGEST-001 |
| `NH-KB-001` Entity Knowledge Base Schema and API | `done` | developer-kb-001 | `knowledge-wiki` | NH-FOUND-003 |
| `NH-KB-002` FTS5 Search | `done` | developer-kb-002 | `knowledge-wiki` | NH-KB-001 |
| `NH-KB-003` On-Demand Wiki Generation | `done` | developer-kb-003 | `knowledge-wiki` | NH-KB-001, NH-LLM-001 |
| `NH-LLM-001` LLM provider interfaces | `done` | developer-llm-001 | `analysis-pipeline` | NH-FOUND-003 |
| `NH-LLM-002` Analysis pipeline | `done` | developer-llm-002 | `analysis-pipeline` | NH-LLM-001, NH-INGEST-002 |
| `NH-PORT-001` Export: Markdown Novel, JSON KB, Markdown Wiki | `done` | developer-port-001 | `portability-resilience` | NH-KB-001, NH-KB-003 |
| `NH-PORT-002` Backup ZIP with Manifest/Checksum, Restore with Validation | `done` | developer-port-002 | `portability-resilience` | NH-PORT-001 |
| `NH-READ-001` Reader UI and navigation | `done` | developer-read-001 | `ingestion-reader` | NH-INGEST-002, NH-FOUND-001 |
| `NH-READ-002` Bookmarks and progress persistence | `done` | developer-read-002 | `ingestion-reader` | NH-READ-001 |

## Queued / proposed

| Task | State | Owner | Milestone | Dependencies |
|------|-------|-------|-----------|--------------|
| `NH-INGEST-005` Frontend Source Management, Import Flow, and Chapter Handler UI | `proposed` | unassigned | `external-ingestion` | NH-INGEST-003 |

## Active ownership

| Task | Branch | Owned paths |
|------|--------|-------------|
| `NH-INGEST-003` | `feat/NH-INGEST-003-ingestion` | `backend/app/scraper.py`<br>`backend/app/routers/sources.py`<br>`backend/app/routers/chapters.py`<br>`backend/app/crud.py`<br>`backend/app/schemas.py`<br>`backend/app/migrations.py`<br>`backend/pyproject.toml` |

## Decisions and blockers

None recorded.

## Next valid action

Assign `NH-FOUND-001` to a Developer and record its branch and owned paths.
