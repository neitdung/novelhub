# NH-HARNESS-001 — Bootstrap and validate the AI engineering harness

## Metadata

- Milestone: `harness-bootstrap`
- Priority: P0
- Weight: 5
- Dependencies: none
- ADRs: `ADR-0001`

## Problem and outcome

AI-assisted work needs durable roles, state, handoffs, verification, and recovery before product implementation starts. The outcome is a dependency-free repository harness that makes current state and next work discoverable.

## In scope

- Agent instructions and role prompts.
- Roadmap, backlog, generated status, task packets, reports, and ADR structure.
- Backlog/state/artifact/ownership validation.
- Status rendering and task checking.
- Stable Make and CI commands.
- Detailed phase plan.

## Out of scope

- Backend or frontend application scaffolding.
- Automatic agent-provider invocation.
- Git repository initialization or remote setup.

## Acceptance criteria

- [x] `make harness-check` validates the committed state.
- [x] `make status` renders task state and milestone progress.
- [x] `make task-check ID=NH-HARNESS-001` validates required completion artifacts.
- [x] Active overlapping owned paths are rejected.
- [x] Illegal task history transitions are rejected.
- [x] Phase documents define objectives, scope, verification, and exit criteria.
- [x] CI runs harness validation first.

## Verification commands

```bash
make harness-check
make status
make task-check ID=NH-HARNESS-001
make ci
```

## Security, privacy, and data safety

Harness artifacts must not contain credentials, private novel text, or machine secrets.

## Compatibility and rollback

The bootstrap uses Python standard library and Make. Removal is file-only and does not affect user data.

## Documentation impact

Resolved by repository README, AGENTS instructions, role prompts, and phase documents.

## Completion evidence

- `.agents/handoffs/NH-HARNESS-001.md`
- `.agents/reports/NH-HARNESS-001-qa.md`
- `.agents/reports/NH-HARNESS-001-review.md`
