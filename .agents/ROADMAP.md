# NovelHub Roadmap

| Milestone | State | Exit summary |
|-----------|-------|--------------|
| `harness-bootstrap` | complete | Agent workflow, state validation, commands, and sample lifecycle work |
| `foundation` | active | Runnable backend/frontend shells and executable contracts |
| `ingestion-reader` | queued | Upload, chapter parsing, bookshelf, reader, progress, bookmarks |
| `analysis-pipeline` | queued | LLM clients and resumable deterministic extraction |
| `knowledge-wiki` | queued | Entity KB, evidence, search, and on-demand wiki |
| `core-frontend` | queued | Accessible primary workflows and resilient realtime UX |
| `discovery-chat` | queued | Cited chat, graph, timeline, and discovery |
| `portability-resilience` | queued | Export, backup/restore, settings, and fault recovery |
| `hardening-release` | queued | Multilingual hardening, packaging, documentation, release |

Detailed scopes and exit criteria are under `docs/plans/`.

## Dependency chain

```text
harness-bootstrap
  → foundation
  → ingestion-reader
  → analysis-pipeline
  → knowledge-wiki
  → core-frontend
  → discovery-chat
  → portability-resilience
  → hardening-release
```

Tasks inside a milestone may run in parallel only when dependencies and path ownership permit it.
