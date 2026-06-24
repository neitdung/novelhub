# Phase 3 — LLM Providers and Analysis Pipeline

## Objective

Implement a deterministic, resumable extraction pipeline optimized for local 16K-context models.

## Scope

- Uniform Ollama, OpenAI-compatible, and Anthropic client interfaces.
- Provider health check, timeout, cancellation, retry classification, and usage accounting.
- Context-budget scaling, chapter chunking, prior-context summaries, prompt versioning.
- Structured extraction for the 11 entity/fact types.
- JSON extraction, normalization, truncated-output repair, and schema validation.
- Processing queue, phase transitions, logs, retry counters, and crash recovery.
- Deterministic reduction: exact match, fuzzy match, and knowledge-base reconciliation.
- Entity evolution and relation/claim deduplication.

## Safety and privacy

- Local provider is default.
- Cloud providers require explicit configuration and UI disclosure.
- API keys never enter Redux persistence, logs, reports, or backups.
- Recorded tests use synthetic text only.

## Deterministic test strategy

- Fake LLM supports success, malformed JSON, truncation, timeout, rate limit, and cancellation.
- Golden extraction fixtures cover Chinese, Vietnamese, and English.
- Pipeline restart tests kill work between every durable phase.
- Idempotency tests ensure retries do not duplicate facts or entities.

## Exit criteria

- A selected chapter range can analyze, pause, resume, cancel, and retry.
- The pipeline recovers after process restart.
- Malformed model output produces repaired data or an actionable chapter error.
- No real network/model dependency is required for merge tests.
