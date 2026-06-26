---
name: qa-task
description: Independently validate a NovelHub task against its observable acceptance criteria using reproducible scenarios, negative cases, focused commands, and regression checks. Results are posted as PR comments. Use when a task reaches dev_complete, when a defect fix requires retesting, or when milestone behavior needs independent verification.
---

# QA Task

## Load context

Read `AGENTS.md`, the QA role description, task packet, developer handoff, and
user-visible contracts. Treat the task packet as authority.

## Validate

1. Confirm the implementation is available in the PR branch.
2. Check out the PR branch:
   ```bash
   git fetch origin
   git checkout <branch-name>
   ```
3. Run task-declared commands independently.
4. Test every acceptance criterion.
5. Add negative, boundary, persistence, cancellation, and recovery scenarios
   where relevant.
6. Run targeted regressions around changed behavior.
7. Treat flaky, skipped, or unexplained failures as failures.
8. Write `.agents/reports/<id>-qa.md` with verdict `pass` or `fail`.
9. Post the QA report as a comment on the PR:
   ```bash
   gh pr comment <pr-number> --body "<!-- qa-report -->\n\n$(cat .agents/reports/<id>-qa.md)"
   ```

## Failure handling

If QA fails (verdict `fail`):
- Request changes on the PR:
  ```bash
  gh pr review <pr-number> --request-changes --body "QA failed - see comment above"
  ```
- Update BACKLOG.yaml state to `qa_failed` for Developer rework.

## Boundaries

Do not fix production code during validation. Do not reinterpret incomplete
criteria in the Developer's favor. Missing evidence is not a pass.

## Output

Record environment, exact commands, criterion-level evidence, defects with
reproduction steps, and residual risks. PR comment with QA report.
