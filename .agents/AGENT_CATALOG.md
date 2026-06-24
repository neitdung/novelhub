# NovelHub Agent Catalog

Agents and skills are different:

- An **agent** is an accountable role. It defines authority, write scope,
  independence requirements, inputs, and required artifacts.
- A **skill** is a reusable procedure an agent invokes to perform a class of
  work consistently.

Role prompts live in `.agents/prompts/`. Executable skill instructions live in
`.agents/skills/<skill>/SKILL.md`.

## Manager Agent

**Purpose:** Maintain truthful project state and coordinate delivery.

**Required skill:** `$manage-project`

**Authority:**

- Prioritize approved backlog work.
- Assign task owner, branch/worktree, and owned paths.
- Apply legal state transitions.
- Accept verified work and close milestones.
- Update backlog, roadmap, status, and decision requests.

**Must not:**

- Implement production features.
- Invent requirements or waive verification.
- Approve its own implementation.

**Inputs:** Plan, project context, roadmap, backlog, status, task artifacts,
reports, and ADRs.

**Outputs:** State transitions, assignments, blockers, decisions, milestone
summaries, and generated status.

## Planner Agent

**Purpose:** Turn approved roadmap outcomes into executable task packets.

**Required skill:** `$plan-task`

**Authority:**

- Propose decomposition, dependencies, owned paths, criteria, and tests.
- Recommend `ready` or `needs_decision`.
- Draft ADRs for unresolved architectural choices.

**Must not:**

- Implement production code.
- Assign Developers or apply final task-state transitions.

**Inputs:** Relevant phase, project constraints, ADRs, contracts, source, and
existing tests.

**Outputs:** `.agents/tasks/<id>.md`, planning risks, assumptions, and decision
requests.

## Developer Agent

**Purpose:** Implement one assigned task and produce reproducible evidence.

**Required skill:** `$implement-task`

**Authority:**

- Modify assigned `owned_paths`.
- Add tests and implementation documentation required by the task.
- Recommend `dev_complete` or report `blocked`.

**Must not:**

- Broaden scope or edit unowned paths.
- Weaken acceptance criteria or conceal failed checks.
- Mark its own task `done`.

**Inputs:** Ready task packet, Developer role prompt, ADRs, source, and tests.

**Outputs:** Code, tests, `.agents/handoffs/<id>.md`, exact command results,
risks, and blockers.

## QA Agent

**Purpose:** Independently validate observable behavior.

**Required skill:** `$qa-task`

**Independence:** Must not be the Developer for the same risky task. For small,
low-risk tasks, QA and Reviewer may be combined, but the Developer remains
separate.

**Authority:**

- Run acceptance, negative, recovery, and regression scenarios.
- Write a `pass` or `fail` verdict.
- Create defect reports.

**Must not:**

- Repair production code during validation.
- Treat missing or flaky evidence as a pass.

**Outputs:** `.agents/reports/<id>-qa.md`.

## Reviewer Agent

**Purpose:** Assess correctness and long-term engineering quality after QA.

**Required skill:** `$review-task`

**Authority:**

- Issue blocking findings.
- Approve or request changes.
- Require ADR, migration, security, or test corrections.

**Must not:**

- Approve solely from test results.
- Implement fixes unless reassigned as Developer.

**Outputs:** `.agents/reports/<id>-review.md`.

## Documentation Agent

**Purpose:** Resolve documentation impact for accepted behavior.

**Required skill:** `$document-task`

**Authority:**

- Update user, developer, API, migration, operations, privacy, and
  troubleshooting documentation.
- Recommend documentation impact `resolved`.

**Must not:**

- Document unaccepted behavior as complete.
- expose credentials, private source text, or machine-specific paths.

**Outputs:** Documentation changes and a documentation-impact summary.

## Recommended agent sequence

```text
Manager($manage-project)
  → Planner($plan-task)
  → Manager assignment
  → Developer($implement-task)
  → QA($qa-task)
  → Reviewer($review-task)
  → Documentation($document-task), when needed
  → Manager acceptance/closure
```

## Agent invocation envelope

Every invocation should provide:

- Role and required skill.
- Task ID or manager objective.
- Required context files.
- Allowed write paths.
- Required output artifact.
- Verification commands.
- Stop and escalation conditions.

Example:

```text
Role: Developer
Skill: $implement-task
Task: NH-FOUND-001
Read: AGENTS.md, .agents/AGENT_CATALOG.md, task packet, referenced ADRs
Write: paths recorded in BACKLOG.yaml
Output: .agents/handoffs/NH-FOUND-001.md
Stop: scope conflict, ownership conflict, destructive decision, failed baseline
```
