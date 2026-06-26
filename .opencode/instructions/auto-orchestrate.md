# Auto-Orchestrate NovelHub Workflow

When the user asks for any **task work** (implementing a feature, fixing a bug, creating a task, etc.), automatically run the **full NovelHub pipeline** without requiring them to specify each role:

## Trigger keywords
Any prompt containing: "task", "feature", "implement", "build", "add", "create", "fix", "new" + project context

## Pipeline sequence

Run each step sequentially. Do NOT skip steps. Do NOT ask the user to confirm between steps.

| Step | Role | What to do |
|------|------|-----------|
| 1 | **Manager** | Run `make harness-check`. Check current state, milestone, backlog. Determine task ID and dependencies. If no task packet exists, proceed to Planner. |
| 2 | **Planner** | Read the relevant phase doc. Decompose the request into a `.agents/tasks/<id>.md` task packet with acceptance criteria, owned paths, dependencies, verification commands. |
| 3 | **Developer** | Read the task packet. Read affected source/tests/ADRs. Implement the smallest change satisfying every criterion. Add/update tests. Run all declared checks. Write `.agents/handoffs/<id>.md`. |
| 4 | **QA** | Read the task packet and handoff. Independently validate every acceptance criterion. Run negative/edge/regression scenarios. Write `.agents/reports/<id>-qa.md` with verdict `pass` or `fail`. |
| 5 | **Reviewer** | Read the task packet, handoff, QA report, and the diff. Review for correctness, architecture fit, security, test quality. Write `.agents/reports/<id>-review.md` with verdict `approve` or `changes_requested`. |
| 6 | **Docs** | Update any needed documentation. Resolve docs impact. |
| 7 | **Manager close** | Run `make status-write`. Run `make harness-check`. Summarize what was done. |

## Harness gates at each step

- Before any state change: `make harness-check`
- Before reading remote state: `make sync-pull`
- After state changes: `make sync-push`, then `make harness-check`

## Artifacts required per gate

| State | Artifact |
|-------|----------|
| `ready` | Task packet exists in `.agents/tasks/<id>.md` |
| `dev_complete` | Handoff exists in `.agents/handoffs/<id>.md` |
| `qa_passed` | QA report exists in `.agents/reports/<id>-qa.md` with `pass` |
| `accepted` | Review report exists in `.agents/reports/<id>-review.md` with `approve` |
| `done` | All prior artifacts + docs impact resolved |

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
