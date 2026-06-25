# NH-LLM-001 — LLM provider interfaces

## Metadata

- Milestone: `analysis-pipeline`
- Priority: P0
- Weight: 5
- Owner: unassigned
- Dependencies: `NH-FOUND-003`
- Proposed owned paths: `backend/`
- ADRs: none

## Problem and outcome

Create uniform interfaces for Ollama, OpenAI-compatible, and Anthropic LLM providers with health checks, retries, and usage tracking.

## In scope

- Provider abstract base class
- Ollama client implementation
- OpenAI-compatible client implementation
- Anthropic client implementation
- Health check, timeout, retry logic
- Usage accounting (tokens, cost)
- Fake LLM for testing

## Out of scope

- Analysis pipeline (NH-LLM-002)
- Frontend integration
- Provider configuration UI

## Acceptance criteria

- [ ] All three provider types can be instantiated
- [ ] Health check works for each provider
- [ ] Fake LLM supports success, error, and timeout scenarios
- [ ] Usage tracking records tokens and cost
- [ ] Retry logic handles transient failures

## Verification commands

```bash
make backend-test
```

## Documentation impact

Pending.
