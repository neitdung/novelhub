---
name: implement-task
description: Implement one ready NovelHub task within assigned ownership boundaries, including tests, focused verification, regression checks, branch creation, PR creation, and a structured developer handoff. Use when acting as the Developer for an assigned task in state ready or in_progress, including rework after QA or review findings.
---

# Implement Task

## Preconditions

Read `AGENTS.md`, the Developer role description, assigned task packet,
referenced ADRs, affected source, and related tests. Confirm the task is
`ready`, `in_progress`, `qa_failed`, or `review_failed`.

## Execute

1. Run `make harness-check` and inspect the baseline.
2. Confirm assigned owner, branch, and owned paths.
3. Create or switch to the assigned branch with proper prefix:
   - Prefix: `feat/`, `fix/`, `chore/`, `docs/`, `refactor/`
   - Pattern: `<prefix>/<task-id>-<short-description>`
   - Example: `feat/NH-HARNESS-002-branch-pr-workflow`
   - Command: `git checkout -b <branch-name>` (create new) or
     `git checkout <branch-name>` (existing)
4. Search for existing conventions and implementation before adding code.
5. Implement the smallest change satisfying every acceptance criterion.
6. Add tests for success, failure, and relevant edge cases.
7. Run all task-declared commands and applicable `make check` gates.
8. Do not hide failures; resolve them or report a blocker.
9. Commit changes with a descriptive message:
   ```bash
   git add <changed-files>
   git commit -m "[NH-XXX-###] Description of changes"
   git push origin <branch-name>
   ```
10. Create a PR that closes the task:
    ```bash
    gh pr create --title "[NH-XXX-###] Title" \
      --body "Closes #<issue-num>" \
      --base main
    ```
11. Write `.agents/handoffs/<id>.md` from the template.
12. Return changed paths, PR URL, checks, risks, blockers, and recommend
    `dev_complete`.

## Fix loop (QA/Review failure)

If QA or Review fails on the PR:
1. Switch back to the task branch: `git checkout <branch-name>`
2. Fix the issues.
3. Commit and push.
4. Update the handoff if needed.
5. Comment on the PR to continue the cycle.

## Boundaries

Do not broaden scope, edit unowned paths, weaken tests, change accepted
architecture, or mark the task complete. Escalate unexplained workspace
changes and requirement conflicts.
