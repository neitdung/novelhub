# Phase 6 — Discovery, Visualization, and Chat

## Objective

Add higher-level exploration through cited chat, relationship graphs, and timelines.

## Scope

- Conversation CRUD, persisted messages, streaming assistant responses, and Markdown export.
- Chat tools for wiki search, page retrieval, entity timelines, chapter status, and processing.
- Mandatory source citations and explicit unsupported-answer behavior.
- Force-directed knowledge graph with filters, shortest path, and entity drill-down.
- Timeline swimlanes with event type, importance, chapter range, and participant linking.
- Wiki link graph and backlink analysis.
- Lazy-load visualization bundles and cap/aggregate very large datasets.

## Security

- Tool calls are allowlisted and validated.
- Chat cannot execute arbitrary SQL, filesystem operations, or shell commands.
- Novel text sent to configured cloud providers follows explicit user settings.
- Rendered Markdown sanitizes unsafe HTML and URLs.

## Verification

- Fake streaming provider tests cancellation, reconnect, partial tokens, and tool errors.
- Citation verifier rejects missing or invalid source references.
- Graph shortest-path and filter logic have deterministic unit tests.
- Performance fixtures cover large entity and event sets.

## Exit criteria

- Chat answers can be audited through valid chapter/wiki citations.
- Graph and timeline remain interactive at the documented dataset limit.
- Unsafe tool and Markdown inputs are rejected or sanitized.
