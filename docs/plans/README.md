# NovelHub Delivery Plan

The original feature plan is split into gated phases. A phase starts only after the preceding phase exit criteria are accepted. Roadmap rows are not direct implementation assignments; the Planner decomposes them into task packets.

| Phase | Outcome | Depends on |
|------:|---------|------------|
| 0 | AI engineering harness and repository governance | None |
| 1 | Backend/frontend foundations and executable API contracts | Phase 0 |
| 2 | Novel ingestion, chapter management, and reader foundation | Phase 1 |
| 3 | LLM providers and deterministic analysis pipeline | Phase 2 |
| 4 | Entity knowledge base, search, and wiki generation | Phase 3 |
| 5 | Real-time analysis UX and core product pages | Phase 4 |
| 6 | Chat, graph, timeline, and advanced discovery | Phase 5 |
| 7 | Export, backup/restore, settings, and resilience | Phase 6 |
| 8 | Hardening, multilingual validation, packaging, and release | Phase 7 |

## Phase documents

- [Phase 0 — AI Engineering Harness](phase-00-harness.md)
- [Phase 1 — Foundation and Contracts](phase-01-foundation.md)
- [Phase 2 — Ingestion and Reader](phase-02-ingestion-reader.md)
- [Phase 3 — LLM and Analysis Pipeline](phase-03-analysis-pipeline.md)
- [Phase 4 — Knowledge Base and Wiki](phase-04-knowledge-wiki.md)
- [Phase 5 — Core Frontend and Realtime](phase-05-core-frontend.md)
- [Phase 6 — Discovery and Chat](phase-06-discovery-chat.md)
- [Phase 7 — Data Portability and Resilience](phase-07-portability-resilience.md)
- [Phase 8 — Hardening and Release](phase-08-hardening-release.md)
- [Cross-phase Technical Reference](technical-reference.md)

## Cross-phase rules

- Chakra UI is the only component/theme system.
- Redux Toolkit and RTK Query own global client state and server cache.
- SQLite migrations are forward-only and tested from empty and previous schemas.
- Real LLM tests are opt-in; merge gates use deterministic fakes and recorded fixtures.
- Novel content stays local unless the user explicitly configures and approves a cloud provider.
- Every task follows the harness state machine and independent QA/review flow.
