# NH-HARNESS-001 — Developer Handoff

## Summary

Created a repository-local AI engineering harness, detailed phase plan, role contracts, backlog/state model, validation scripts, Make commands, and CI gate.

## Changed paths

- `AGENTS.md`
- `.agents/`
- `scripts/harness/`
- `docs/plans/`
- `Makefile`
- `.github/workflows/ci.yml`

## Acceptance criteria evidence

- Harness state and artifacts are validated by `scripts/harness/check_state.py`.
- Status is derived from the backlog by `scripts/harness/render_status.py`.
- Task-specific completion requirements are checked by `scripts/harness/task_check.py`.
- The canonical plan is `PLAN.md`, which links all phase documents.

## Verification

| Command | Expected |
|---------|----------|
| `make harness-check` | Pass |
| `make status` | Render dashboard |
| `make task-check ID=NH-HARNESS-001` | Pass |
| `make ci` | Pass |

## Risks and follow-up

- Git is not initialized; branches/worktrees become enforceable after repository initialization.
- The first foundation task has an explicit package-manager decision before assignment.
