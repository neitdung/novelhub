---
name: implement-task
description: Implement one ready NovelHub task within assigned ownership boundaries, including tests, focused verification, regression checks, and a structured developer handoff. Use when acting as the Developer for an assigned task in state ready or in_progress, including rework after QA or review findings.
---

# Implement Task

## Preconditions

Read `AGENTS.md`, the Developer role description, assigned task packet,
referenced ADRs, affected source, and related tests. Confirm the task is
`ready`, `in_progress`, `qa_failed`, or `review_failed`.

## Execute

1. Run `make harness-check` and inspect the baseline.
2. Confirm assigned owner, branch, and owned paths.
3. Search for existing conventions and implementation before adding code.
4. Implement the smallest change satisfying every acceptance criterion.
5. Add tests for success, failure, and relevant edge cases.
6. Run all task-declared commands and applicable `make check` gates.
7. Do not hide failures; resolve them or report a blocker.
8. Write `.agents/handoffs/<id>.md` from the template.
9. Return changed paths, checks, risks, blockers, and recommend
   `dev_complete`.

## Boundaries

Do not broaden scope, edit unowned paths, weaken tests, change accepted
architecture, or mark the task complete. Escalate unexplained workspace
changes and requirement conflicts.
