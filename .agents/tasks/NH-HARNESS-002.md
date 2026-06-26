# NH-HARNESS-002: Branch Naming, PR Creation, and PR-Based Review Workflow

## Outcome

The agent workflow instructions are updated to require branch creation with
proper prefixes (feat, fix, chore, etc.), PR creation for task completion, and
PR-based QA/Review workflow before merging to main.

## Scope

Update agent role prompts, skill documents, and workflow instructions to include
branch naming conventions, PR creation steps, and PR-based review flow.

### In scope

- Add branch naming convention (prefix: feat/, fix/, chore/, docs/, refactor/) to
  Developer workflow and Planner task-packet template.
- Add `git checkout -b` step to Developer flow before implementation.
- Add `gh pr create` step to Developer flow after implementation.
- Add `gh pr review` / PR commenting to QA and Reviewer flows.
- Add PR merge step to Manager flow after acceptance.
- Add branch cleanup and `git checkout main` steps to Manager flow.
- Update `.opencode/instructions/auto-orchestrate.md` pipeline.
- Update `AGENTS.md` gh CLI workflow table with PR commands.
- Update `BACKLOG.yaml` to include the new task.

### Out of scope

- CI/CD pipeline changes or GitHub Actions modifications.
- Changes to the harness state machine (`check_state.py`).
- Changes to the sync scripts.

## Dependencies

- `NH-HARNESS-001` (done) — existing harness bootstrap.

## Owned paths

- `.agents/prompts/developer.md`
- `.agents/prompts/manager.md`
- `.agents/prompts/planner.md`
- `.agents/prompts/qa.md`
- `.agents/prompts/reviewer.md`
- `.agents/skills/implement-task/SKILL.md`
- `.agents/skills/manage-project/SKILL.md`
- `.agents/skills/qa-task/SKILL.md`
- `.agents/skills/review-task/SKILL.md`
- `.agents/skills/plan-task/SKILL.md`
- `AGENTS.md`
- `.opencode/instructions/auto-orchestrate.md`
- `.agents/BACKLOG.yaml`

## Architecture and ADR constraints

None. This is a workflow/process change only.

## Acceptance criteria

1. **Branch naming convention**: Developer prompt/skill requires branch names
   with a prefix (`feat/`, `fix/`, `chore/`, `docs/`, `refactor/`) followed by
   the task ID (e.g., `feat/NH-HARNESS-002-branch-pr-workflow`).

2. **Branch creation before implementation**: Developer flow includes
   `git checkout -b <branch-name>` before making changes.

3. **PR creation after implementation**: Developer flow includes
   `gh pr create` to create a PR that closes the issue/task after
   implementation is complete.

4. **PR-based QA**: QA flow describes commenting on the PR with the QA report
   rather than on the Issue.

5. **PR-based Review**: Reviewer flow describes commenting on the PR with the
   review report.

6. **Manager PR merge**: Manager flow includes steps to merge the PR, switch
   back to main, pull latest, and clean up the branch.

7. **Loop on failure**: If QA or Review fails on the PR, the Developer returns
   to the branch, fixes, pushes, and the cycle continues.

8. **Auto-orchestrate pipeline updated**: `.opencode/instructions/auto-orchestrate.md`
   reflects the branch/PR workflow.

9. **AGENTS.md updated**: The gh CLI commands table includes `gh pr create`,
   `gh pr review`, `gh pr merge`.

## Verification commands

```bash
make harness-check
# Manual review that the updated files contain the expected branch/PR workflow
grep -l "branch" .agents/prompts/developer.md .agents/skills/implement-task/SKILL.md
grep -l "gh pr" .opencode/instructions/auto-orchestrate.md AGENTS.md
```

## Migration / Rollback

No data migration. Rollback by reverting changed files.

## Documentation impact

`pending` — the agent workflow instructions are the documentation.

## Open questions

None.

## Risks and assumptions

- Assumes the Developer role has write access to create branches and PRs.
- Assumes `gh` CLI is available and authenticated.
