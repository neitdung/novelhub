# ADR-0001 — Repository-local AI engineering harness

- Status: accepted
- Date: 2026-06-25
- Owners: project manager

## Context

AI development sessions are interruptible and may use different agents or providers. Chat history is insufficient as project memory, and concurrent work needs explicit ownership and verification.

## Decision

Store agent roles, tasks, status, handoffs, reports, and decisions in versioned repository files. Use JSON-compatible YAML for backlog state and dependency-free Python scripts for bootstrap validation. Use Make as the stable command interface because `just` is not available in the initial environment.

## Consequences

- A new agent can resume from repository state.
- State transitions and completion artifacts are enforceable in CI.
- Project management introduces some ceremony.
- Git branch/worktree isolation becomes fully active after Git initialization.

## Alternatives considered

- Chat-only state: rejected because it is not durable or reviewable.
- Vendor-specific agent configuration as source of truth: rejected due to lock-in.
- Database-backed orchestration service: deferred as unnecessary for a local project.
