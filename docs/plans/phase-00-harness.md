# Phase 0 — AI Engineering Harness

## Objective

Establish the repository-local operating model for AI-assisted engineering before application scaffolding.

## Deliverables

- Repository instructions and role prompts.
- Persistent product, roadmap, status, task, handoff, report, and ADR artifacts.
- Machine-readable backlog with legal-state validation.
- Active-path ownership conflict detection.
- Generated project dashboard.
- Stable Make commands and CI-first harness validation.
- A completed sample task proving the full workflow.

## Work packages

### P0.1 Governance

- Define Manager, Planner, Developer, QA, Reviewer, and Docs boundaries.
- Define human approval gates and prohibited autonomous actions.
- Define context-loading order and recovery procedure.

### P0.2 State model

- Implement task states and transition rules.
- Require task packets, handoffs, QA reports, and review reports at gates.
- Validate dependencies, unique IDs, artifact paths, and active ownership.

### P0.3 Agent contracts

- Version role prompts.
- Define task packet and structured result formats.
- Define escalation, stop, and rework conditions.

### P0.4 Automation

- Implement `make harness-check`, `make status`, `make task-check`, and `make ci`.
- Ensure bootstrap needs only Python 3.11+ and Make.
- Run harness validation before all application checks in CI.

### P0.5 Workflow proof

- Complete `NH-HARNESS-001` through planning, implementation, QA, review, and acceptance artifacts.
- Leave `NH-FOUND-001` ready as the first real project task.

## Exit criteria

- A new agent can determine current state and next work from repository files only.
- Invalid states, missing artifacts, unknown dependencies, and ownership overlap fail validation.
- Status rendering is deterministic.
- The sample completed task passes `make task-check`.
- CI configuration executes the harness gate first.

## Risks

- Excess ceremony: task packets should remain proportional to risk.
- Stale status: generated sections must derive from backlog state.
- False parallelism: central files and contracts must remain exclusive.
