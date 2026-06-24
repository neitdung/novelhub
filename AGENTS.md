# NovelHub Agent Instructions

## Required startup sequence

Every agent must read:

1. This file.
2. `.agents/PROJECT.md`.
3. `.agents/STATUS.md`.
4. Its role prompt in `.agents/prompts/`.
5. Its assigned task packet in `.agents/tasks/`.
6. Referenced ADRs and directly affected source/tests.

Run `make harness-check` before changing project state.

## Source of truth

- `.agents/BACKLOG.yaml` is the machine-readable project-state source of truth. It is JSON-compatible YAML and is parsed with Python's standard library.
- `.agents/STATUS.md` is a generated human dashboard. Update it with `make status-write`; do not edit generated task tables manually.
- `PLAN.md` is the canonical plan entry point and indexes the approved delivery phases.
- Task packets define implementation scope and acceptance criteria.
- ADRs define accepted cross-cutting architecture decisions.

## Roles

- Manager: state transitions, assignment, priority, conflict handling, milestone closure.
- Planner: task decomposition and acceptance criteria; no production implementation.
- Developer: code and tests within assigned paths.
- QA: independent behavioral validation.
- Reviewer: correctness, architecture, security, and maintainability review.
- Docs: documentation changes after behavior is accepted.

No agent may approve its own implementation. Only the Manager may transition a task to `accepted` or `done`.

## Working rules

- One active Developer task per agent.
- Do not edit outside `owned_paths` without Manager approval.
- Do not overlap active ownership of migrations, schemas, lockfiles, generated contracts, central configuration, or shared state setup.
- Preserve user changes. Stop and report unexplained modifications in owned paths.
- Search before assuming a file, symbol, route, or convention does not exist.
- Add or update tests with behavior changes.
- Record exact verification commands and outcomes in the handoff.
- Never commit secrets, credentials, private novel content, local model prompts containing user text, or machine-specific paths.
- Human approval is required for destructive data operations, irreversible migrations, paid/cloud dependencies, external transmission of novel content, scope changes, and releases.

## Task flow

`proposed → planning → ready → in_progress → dev_complete → qa_passed → accepted → done`

Permitted loops and exceptional states are enforced by `scripts/harness/check_state.py`.

Required artifacts:

- `ready`: task packet exists.
- `dev_complete`: developer handoff exists.
- `qa_passed`: passing QA report exists.
- `accepted`: approved review report exists.
- `done`: all prior artifacts exist and documentation impact is resolved.

## Stable commands

```bash
make harness-check
make status
make status-write
make task-check ID=<task-id>
make check
make integration
make e2e
make ci
```

Commands must be non-interactive and return non-zero on failure.
