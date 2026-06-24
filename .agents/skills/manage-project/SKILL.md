---
name: manage-project
description: Coordinate NovelHub project execution through backlog triage, legal task-state transitions, ownership assignment, blocker handling, milestone progress, and acceptance gates. Use when selecting the next task, assigning work, updating project state, resolving workflow conflicts, accepting verified work, or closing a milestone.
---

# Manage Project

## Load context

Read `AGENTS.md`, `.agents/PROJECT.md`, `.agents/ROADMAP.md`,
`.agents/STATUS.md`, `.agents/BACKLOG.yaml`, and relevant task artifacts.
Read `PLAN.md` when milestone scope or exit criteria matter.

## Execute

1. Run `make harness-check`.
2. Identify the requested objective and active milestone.
3. Reject or escalate work outside approved scope.
4. Select only tasks whose dependencies are `accepted` or `done`.
5. Require a complete task packet before moving work to `ready`.
6. Assign one owner, branch/worktree, and non-overlapping owned paths.
7. Apply only transitions allowed by the harness state machine.
8. At each gate, verify required artifacts and command evidence.
9. Regenerate status with `make status-write`.
10. Run `make harness-check` after state changes.

## Gate rules

- Move to `dev_complete` only when a handoff exists.
- Move to `qa_passed` only when QA records `pass`.
- Move to `accepted` only when review records `approve`.
- Move to `done` only when documentation impact is `none` or `resolved`.
- Do not accept an agent's own implementation without independent QA/review.

## Escalate

Ask the user before product/architecture scope changes, destructive data
operations, external content transmission, paid dependencies, breaking
contracts, or release.

## Output

Update `.agents/BACKLOG.yaml`, regenerate `.agents/STATUS.md`, and state the
decision, current blockers, and next valid action.
