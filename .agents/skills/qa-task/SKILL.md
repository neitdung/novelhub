---
name: qa-task
description: Independently validate a NovelHub task against its observable acceptance criteria using reproducible scenarios, negative cases, focused commands, and regression checks. Use when a task reaches dev_complete, when a defect fix requires retesting, or when milestone behavior needs independent verification.
---

# QA Task

## Load context

Read `AGENTS.md`, the QA role description, task packet, developer handoff, and
user-visible contracts. Treat the task packet as authority.

## Validate

1. Confirm the implementation is available in a reproducible environment.
2. Run task-declared commands independently.
3. Test every acceptance criterion.
4. Add negative, boundary, persistence, cancellation, and recovery scenarios
   where relevant.
5. Run targeted regressions around changed behavior.
6. Treat flaky, skipped, or unexplained failures as failures.
7. Write `.agents/reports/<id>-qa.md` with verdict `pass` or `fail`.

## Boundaries

Do not fix production code during validation. Do not reinterpret incomplete
criteria in the Developer's favor. Missing evidence is not a pass.

## Output

Record environment, exact commands, criterion-level evidence, defects with
reproduction steps, and residual risks.
