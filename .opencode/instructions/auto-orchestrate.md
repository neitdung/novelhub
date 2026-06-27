# Auto-Orchestrate NovelHub Workflow

When the user asks for any **task work** (implementing a feature, fixing a bug, creating a task, etc.), automatically run the **full NovelHub pipeline** without requiring them to specify each role:

## Trigger keywords
Any prompt containing: "task", "feature", "implement", "build", "add", "create", "fix", "new" + project context

## Precondition: GitHub token

Before any task work, check if `gh` CLI is authenticated:
- Run `gh auth status` to verify.
- If not authenticated, tell the user: `GITHUB_TOKEN` must be set in `.env` or via `gh auth login`.

## Pipeline sequence

Run each step sequentially. Do NOT skip steps. Do NOT ask the user to confirm between steps.

| Step | Role | What to do | GitHub action |
|------|------|-----------|---------------|
| 1 | **Manager** | Run `make harness-check`. Check current state, milestone, backlog. Determine task ID and dependencies. Create the task packet file locally. | `gh issue create --title "[NH-XXX-###] Title" --body "$(cat .agents/tasks/<id>.md)" --label task`. Then `ARGS="--task NH-XXX-###" make sync-push` to set Status→Planning. |
| 2 | **Planner** | Read the relevant phase doc. Decompose the request into a `.agents/tasks/<id>.md` task packet with acceptance criteria, owned paths, dependencies, verification commands. | `gh issue edit <num> --body "$(cat .agents/tasks/<id>.md)"`. Then `ARGS="--task NH-XXX-###" make sync-push` to set Status→Ready. |
| 3 | **Developer** | Read the task packet. Read affected source/tests/ADRs. Create/switch to branch (`git checkout -b <prefix>/<task-id>-<desc>`). Implement the smallest change satisfying every criterion. Add/update tests. Run all declared checks. Commit, push. Create PR. Write `.agents/handoffs/<id>.md`. | `gh issue comment <num> --body "<!-- handoff -->\n\n$(cat .agents/handoffs/<id>.md)"`. `gh pr create --title "[NH-XXX-###] Title" --body "Closes #<issue-num>" --base main`. Update BACKLOG.yaml state, then `ARGS="--task NH-XXX-###" make sync-push` to set Status→Dev Complete. |
| 4 | **QA** | Check out the PR branch. Read the task packet and handoff. Independently validate every acceptance criterion. Run negative/edge/regression scenarios. Write `.agents/reports/<id>-qa.md` with verdict `pass` or `fail`. | `gh pr comment <pr-number> --body "<!-- qa-report -->\n\n$(cat .agents/reports/<id>-qa.md)"`. Update BACKLOG.yaml state, then `ARGS="--task NH-XXX-###" make sync-push` to set Status→QA Passed. |
| 5 | **Reviewer** | Read the task packet, handoff, QA report, and the PR diff. Review for correctness, architecture fit, security, test quality. Write `.agents/reports/<id>-review.md` with verdict `approve` or `changes_requested`. | `gh pr review <pr-number> --approve --body "$(cat .agents/reports/<id>-review.md)"` or `--request-changes`. Update BACKLOG.yaml state, then `ARGS="--task NH-XXX-###" make sync-push` to set Status→Accepted. |
| 6 | **Docs** | Update any needed documentation. Resolve docs impact. | No GitHub action needed. |
| 7 | **Manager close** | Merge PR (`gh pr merge`). Switch to main (`git checkout main`), pull latest, delete branch. Run `gh issue close <num>`. Update BACKLOG.yaml state. Run `make sync-push ARGS="--all"`. Run `ARGS="--task NH-XXX-###" make sync-pull`. Run `make status-write`. Run `make harness-check`. Summarize what was done. | `gh pr merge <pr-number> --merge --subject "[NH-XXX-###] Title"`, `gh issue close <num>`, then `make sync-push ARGS="--all"` to set Status→Done. |

## Harness gates at each step

- Before any state change: `make harness-check`
- Before reading remote state: `make sync-pull`
- After state changes: `make sync-push`, then `make harness-check`

## Artifacts required per gate

| State | GitHub artifact | Local artifact |
|-------|----------------|----------------|
| `planning` | Issue body (task packet), label `task` | `.agents/tasks/<id>.md` |
| `ready` | Updated Issue body | `.agents/tasks/<id>.md` |
| `in_progress` | BACKLOG.yaml sync | Owner set, paths assigned |
| `dev_complete` | `<!-- handoff -->` comment | `.agents/handoffs/<id>.md` |
| `qa_passed` | `<!-- qa-report -->` comment with `pass` | `.agents/reports/<id>-qa.md` with `pass` |
| `accepted` | `<!-- review-report -->` comment with `approve` | `.agents/reports/<id>-review.md` with `approve` |
| `done` | Issue closed, docs impact resolved | All prior artifacts |

## Escalation

Stop and ask the user if:
- The request contradicts project rules or architecture
- The request involves destructive data operations, external content transmission, paid dependencies
- The request is ambiguous in scope
- A step produces a `fail` or `changes_requested` verdict

## Safety

- Never edit files outside the task's `owned_paths` without asking
- Never commit secrets, credentials, or private novel content
- Never mark a task `done` — only the Manager role may do that
