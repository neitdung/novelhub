# NovelHub Technical Reference

This document carries cross-phase details from the consolidated source plan. Phase task packets may refine these contracts through ADRs.

## Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, TypeScript, Next.js (App Router, server mode with API proxy), Chakra UI |
| State | Redux Toolkit, React Redux, RTK Query |
| Routing | Next.js App Router (file-system-based) |
| Forms | React Hook Form, Zod |
| Backend | Python 3.11+, FastAPI async |
| Database | SQLite, aiosqlite, FTS5 |
| Realtime | FastAPI WebSocket |
| LLM | Ollama, OpenAI-compatible, Anthropic |
| NLP | jieba, underthesea, language detection |
| Tests | Pytest, Vitest, React Testing Library, Playwright |

## Core extraction types

The extraction contract covers:

1. Characters
2. Relationships
3. Locations
4. Realms
5. Techniques
6. Item events
7. Organization events
8. Narrative events
9. Spatial relationships
10. Concepts
11. Generic relations

Every extracted record must retain chapter provenance. Relationship and claim evidence must preserve a bounded source excerpt or stable location reference.

## Pipeline phases

### Extract

- One model call per normal chapter for 16K models.
- Inject a bounded summary from prior chapters.
- Validate structured output and normalize field-name/model variations.
- Repair common truncation and fence/thinking-block failures.
- Persist raw response metadata separately from accepted facts.

### Reduce

- Exact normalized-name deduplication.
- Fuzzy candidate generation with a documented threshold.
- Reconciliation against the existing novel knowledge base.
- Deduplicate relations and claims.
- Record entity field evolution by chapter.

### Enrich

- Generate wiki pages only on explicit request.
- Use entity facts, source chapters, current page revision, and language.
- Store Markdown as source of truth with generation metadata and version.

## Initial token budget for 16K context

| Component | Approximate tokens |
|-----------|-------------------:|
| System prompt | 400 |
| Prior context summary | 1,500 |
| Chapter text | 4,000 |
| Extraction schema | 800 |
| Extraction output | 4,000 |
| Total extraction call | 10,700 |

Budgets are runtime-scaled and must reserve enough context for output. The Ollama default cap remains conservative to avoid excessive KV-cache allocation.

## Data domains

### Library

- Novels
- Chapters
- Chapter facts and extraction metadata
- Reading state
- Bookmarks

### Knowledge base

- Entities
- Language-specific names and aliases
- Mentions
- Evolution history
- Relations
- Claims and contradictions

### Wiki and search

- Wiki pages and versions
- Wiki links and backlinks
- FTS5 entity and wiki indexes

### Processing

- Analysis tasks
- Chapter queue
- Phase status and progress
- Retry/error information
- Pipeline log

### Chat and system

- Conversations and messages
- Application settings
- Backup records
- Benchmark history

## API domains

All APIs use `/api` and typed error envelopes.

- `/novels`: list, upload, import/export, metadata, delete, statistics.
- `/novels/{id}/chapters`: chapter list/content, exclusions, entities, reading state, bookmarks.
- `/novels/{id}/analysis`: start, latest status, retry, clear, optional prescan.
- `/analysis/{task_id}`: status and pause/resume/cancel.
- `/novels/{id}/entities`: list, profile, timeline, mentions.
- `/novels/{id}/graph`: graph data and shortest path.
- `/novels/{id}/timeline`: event timeline.
- `/novels/{id}/wiki`: list, get, generate, batch generate, delete, backlinks, search.
- `/novels/{id}/conversations` and `/conversations/{id}`: chat lifecycle and export.
- `/novels/{id}/export`: series bible and templates.
- `/settings`: provider configuration, health, hardware, validation, benchmark.
- `/backup`: export and import.
- `/health`: application health.

WebSocket paths:

- `/ws/analysis/{novel_id}`
- `/ws/chat/{session_id}`

## Frontend ownership

| Data category | Owner |
|---------------|-------|
| Novels, chapters, entities, wiki, graph, timeline, settings | RTK Query |
| Analysis and chat streams | RTK Query cache lifecycle |
| Selected novel, active filters, drafts, reader preferences | Redux slices |
| Dialogs, hover state, temporary UI state | Local React state |
| Form validation and dirty state | React Hook Form |

WebSocket handlers validate messages, update cached data incrementally, reconnect with capped exponential backoff and jitter, and fall back to polling.

## Required indexes and integrity rules

- Chapter uniqueness by novel and chapter number.
- Entity uniqueness by novel, type, and slug.
- Wiki uniqueness by novel, slug, and language.
- Foreign keys enabled with appropriate cascades.
- Index chapter status, entity type/slug, mentions, relations, wiki language/type, queue state, logs, messages, and bookmarks.
- FTS indexes remain synchronized across insert, update, delete, rebuild, backup, and restore.

## Product-wide quality rules

- WCAG 2.2 AA for core workflows.
- Virtualize large chapter/entity/timeline/log lists.
- No API keys in logs, Redux persistence, exports, backups, or harness files.
- No real LLM dependency in merge CI.
- Pipeline and restore operations are resumable or transactional.
- All supported language fixtures complete the P0 workflow before release.
