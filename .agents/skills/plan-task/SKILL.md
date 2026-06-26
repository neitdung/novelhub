---
name: plan-task
description: Convert an approved NovelHub roadmap objective into bounded implementation-ready task packets with dependencies, owned paths, architecture constraints, branch naming conventions, acceptance criteria, verification commands, and risk analysis. Use when decomposing a phase, preparing a proposed task, clarifying implementation scope, or revising a task after requirements change.
---

# Plan Task

## Load context

Read `AGENTS.md`, `PLAN.md`, the relevant phase document, `.agents/PROJECT.md`,
`.agents/STATUS.md`, affected ADRs, and related source/contracts.

## Plan

1. Define one observable outcome.
2. Separate in-scope and out-of-scope work.
3. Identify dependencies and shared-contract prerequisites.
4. Propose narrow owned paths and flag central-file conflicts.
5. Record architecture, privacy, migration, compatibility, and rollback
   constraints.
6. Write acceptance criteria as objective pass/fail statements.
7. Specify exact focused and regression verification commands.
8. Record documentation impact and unresolved decisions.
9. Recommend a branch name with proper prefix when assigning:
   - Prefix: `feat/`, `fix/`, `chore/`, `docs/`, `refactor/`
   - Pattern: `<prefix>/<task-id>-<short-description>`
   - Example: `feat/NH-HARNESS-002-branch-pr-workflow`
10. Create `.agents/tasks/<id>.md` from the task template.
11. Recommend `ready`, `needs_decision`, or further decomposition to the
    Manager.

## Task sizing

Prefer one focused development session. Split work when it spans independent
contracts, migrations, backend/frontend ownership, or unrelated acceptance
paths.

## Stop conditions

Do not implement production code. Stop at `needs_decision` when ambiguity
changes user behavior, data safety, privacy, cost, or architecture.
