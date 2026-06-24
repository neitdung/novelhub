---
name: review-task
description: Review a NovelHub implementation for correctness, architecture fit, data integrity, security, privacy, concurrency, error handling, maintainability, and test quality. Use after QA passes, for risky migrations or backup work, or when assessing whether a task can be accepted.
---

# Review Task

## Load context

Read `AGENTS.md`, the Reviewer role description, task packet, handoff, QA
report, relevant ADRs, and the complete diff.

## Review

1. Verify implementation against each acceptance criterion.
2. Inspect failure paths, idempotency, concurrency, and lifecycle behavior.
3. Check architecture and phase constraints.
4. Check secrets, privacy, input validation, and unsafe external transmission.
5. For data changes, inspect migrations, rollback/recovery, and compatibility.
6. Assess tests for meaningful assertions and regression coverage.
7. Rank findings by severity with precise path/evidence.
8. Write `.agents/reports/<id>-review.md` with verdict `approve` or
   `changes_requested`.

## Boundaries

Do not approve solely because tests pass. Do not implement fixes unless
reassigned as Developer. Any unresolved blocking finding requires rework.
