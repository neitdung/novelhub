# NovelHub Plan

This is the canonical entry point for the NovelHub delivery plan.

## Delivery phases

| Phase | Outcome | Detailed plan |
|------:|---------|---------------|
| 0 | AI engineering harness and repository governance | [Phase 0](docs/plans/phase-00-harness.md) |
| 1 | Backend/frontend foundations and executable API contracts | [Phase 1](docs/plans/phase-01-foundation.md) |
| 2 | Novel ingestion, chapter management, and reader foundation | [Phase 2](docs/plans/phase-02-ingestion-reader.md) |
| 3 | LLM providers and deterministic analysis pipeline | [Phase 3](docs/plans/phase-03-analysis-pipeline.md) |
| 4 | Entity knowledge base, search, and wiki generation | [Phase 4](docs/plans/phase-04-knowledge-wiki.md) |
| 5 | Real-time analysis UX and core product pages | [Phase 5](docs/plans/phase-05-core-frontend.md) |
| 6 | Chat, graph, timeline, and advanced discovery | [Phase 6](docs/plans/phase-06-discovery-chat.md) |
| 7 | Export, backup/restore, settings, and resilience | [Phase 7](docs/plans/phase-07-portability-resilience.md) |
| 8 | Hardening, multilingual validation, packaging, and release | [Phase 8](docs/plans/phase-08-hardening-release.md) |

See the [phase index](docs/plans/README.md) for sequencing rules and the
[technical reference](docs/plans/technical-reference.md) for cross-phase
architecture, data, API, extraction, and quality requirements.

## Active execution state

- [Project context](.agents/PROJECT.md)
- [Roadmap](.agents/ROADMAP.md)
- [Current status](.agents/STATUS.md)
- [Machine-readable backlog](.agents/BACKLOG.yaml)
- [Agent instructions](AGENTS.md)

The phase documents describe approved roadmap scope. Actual development begins
only from a `ready` task packet in `.agents/tasks/`.
