# Phase 4 — Knowledge Base, Search, and Wiki

## Objective

Turn extracted facts into an inspectable, searchable entity knowledge base and on-demand wiki.

## Scope

- Entity profiles, translations/name variants, mentions, relationships, claims, and evolution.
- Alias resolution using normalized exact matching, fuzzy candidates, and auditable merges.
- Entity browser with type filters, mentions, relations, and chapter evidence.
- FTS5 indexes and synchronization for entities and wiki pages.
- On-demand wiki planning and generation with source chapter references.
- Wiki links, backlinks, versions, language selection, and delete/regenerate behavior.
- Optional manual content editing without losing generated-source metadata.

## Data integrity

- Merges preserve source records and can be audited.
- Evidence links point to stable chapter identifiers.
- FTS triggers are tested against insert, update, delete, rebuild, and restore.
- Wiki generation is idempotent by entity, language, prompt version, and source revision.

## Verification

- Search ranking and Unicode tokenizer fixtures.
- Alias merge and false-positive boundary tests.
- Wiki generation with fake LLM and citation validation.
- E2E: analyze fixture → browse entity → inspect evidence → generate/search wiki.

## Exit criteria

- Users can trace every core entity fact to chapter evidence.
- Search returns useful results across all target languages.
- Wiki pages are generated only on demand and remain versioned.
