# NH-HARNESS-002 Developer Handoff

## Summary

Updated agent workflow instructions across role prompts, skill documents, and
workflow instructions to require branch creation with proper prefixes,
PR creation for task completion, and PR-based QA/Review workflow.

## Changes made

### Prompts (`.agents/prompts/`)
- **developer.md**: Added branch naming convention (`feat/`, `fix/`, `chore/`,
  `docs/`, `refactor/`), `git checkout -b` before implementation, `gh pr create`
  after implementation, and fix-loop instructions for QA/Review failures.
- **manager.md**: Added PR merge steps (`gh pr merge`, `git checkout main`,
  `git pull origin main`, `git branch -d`).
- **planner.md**: Added branch naming recommendation when assigning tasks.
- **qa.md**: Changed to PR-based QA (`gh pr comment` instead of `gh issue comment`),
  added `gh pr review --request-changes` for failures.
- **reviewer.md**: Changed to PR-based review (`gh pr review --approve` or
  `--request-changes`).

### Skills (`.agents/skills/*/SKILL.md`)
- **implement-task/SKILL.md**: Added step 3 (branch creation), step 9-10 (commit,
  push, PR creation), and fix-loop section for QA/Review failures.
- **manage-project/SKILL.md**: Added step 9 (PR merge workflow), branch naming
  suggestions in step 6, updated gate rules to mention PR/merge.
- **qa-task/SKILL.md**: Added PR branch checkout, PR comment posting,
  failure-handling with `gh pr review --request-changes`.
- **review-task/SKILL.md**: Added PR review posting (`--approve`, `--request-changes`),
  failure handling section.
- **plan-task/SKILL.md**: Added step 9 for branch naming recommendation.

### Workflow documentation
- **AGENTS.md**: Added "Branch naming convention" section with prefix table,
  added `Create/switch branch`, `gh pr create`, `gh pr comment`, `gh pr review`,
  `gh pr merge` to gh CLI commands table. Updated Required artifact flow table
  to include branch/PR actions.
- **.opencode/instructions/auto-orchestrate.md**: Updated Developer step with
  branch creation/PR creation. Updated QA/Reviewer to use PR-based comments.
  Updated Manager close with PR merge, main switch, branch cleanup.

### Project state
- **.agents/tasks/NH-HARNESS-002.md**: Created task packet.
- **.agents/BACKLOG.yaml**: Added NH-HARNESS-002 task entry.

## Verification

```bash
make harness-check
```

## Risks and blockers

None. This is a process-only change to agent instructions; no production code
is affected.

## Verification commands

```bash
make harness-check
grep -c "branch" .agents/prompts/developer.md .agents/skills/implement-task/SKILL.md
grep -c "gh pr" .opencode/instructions/auto-orchestrate.md AGENTS.md
```

## Acceptance criteria verification

| Criterion | Status |
|-----------|--------|
| 1. Branch naming convention in Developer prompt/skill | ✅ Done |
| 2. Branch creation before implementation | ✅ Done |
| 3. PR creation after implementation | ✅ Done |
| 4. PR-based QA | ✅ Done |
| 5. PR-based Review | ✅ Done |
| 6. Manager PR merge | ✅ Done |
| 7. Loop on failure | ✅ Done |
| 8. Auto-orchestrate pipeline updated | ✅ Done |
| 9. AGENTS.md updated with PR commands | ✅ Done |

## Recommend

`dev_complete`
