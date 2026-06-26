# NovelHub Agent Instructions

## Required startup sequence

Every agent must read:

1. This file.
2. `.agents/PROJECT.md`.
3. `.agents/AGENT_CATALOG.md`.
4. `.agents/STATUS.md`.
5. Its role prompt in `.agents/prompts/`.
6. Its required skill in `.agents/skills/<skill>/SKILL.md`.
7. Its assigned task packet — read from the **GitHub Issue** via `gh` CLI.
8. Referenced ADRs and directly affected source/tests.

Run `make harness-check` before changing project state.

## Source of truth

- **GitHub Issues** are the primary source of truth for tasks, handoffs, QA reports, and review reports.
- **GitHub Project** custom fields hold state, milestone, priority, weight, owner, and dependencies.
- `.agents/BACKLOG.yaml` is a **generated snapshot** of the current Issue state. Do not edit directly — run `make sync-pull` to regenerate.
- `.agents/STATUS.md` is a generated human dashboard. Regenerate with `make status-write` after a sync.
- **[NovelHub GitHub Project](https://github.com/neitdung/novelhub/projects)** is the human-readable project board.
- `PLAN.md` is the canonical plan entry point and indexes the approved delivery phases.
- Task packets define implementation scope and acceptance criteria.
- ADRs define accepted cross-cutting architecture decisions (stored as Issues with `adr` label).

### Issue format

Each task is a GitHub Issue with:

| Element | Format |
|---------|--------|
| **Title** | `[NH-XXX-###] Task Title` |
| **Body** | Full task packet (.md format) |
| **Label** | `task` |
| **Project field `State`** | Task state (Proposed, Planning, Ready, In Progress, etc.) |
| **Project field `Milestone`** | Milestone name from ROADMAP.md |
| **Project field `Priority`** | P0/P1/P2/P3 |
| **Project field `Weight`** | Numeric 1-13 |
| **Project field `Owner`** | GitHub username or role |
| **Project field `Task ID`** | The `NH-XXX-###` identifier (used to match in sync) |
| **Comments** | Artifacts prefixed with HTML markers (see below) |

### Comment markers for artifacts

| Artifact | Comment marker |
|----------|---------------|
| Developer handoff | `<!-- handoff -->` at start of comment body |
| QA report | `<!-- qa-report -->` at start of comment body |
| Review report | `<!-- review-report -->` at start of comment body |

### Setting up the GitHub Project

1. Create a new GitHub Project (Project v2) in the `neitdung` org or your personal account.
2. Add these custom fields:

   | Field name | Type | Options |
   |------------|------|---------|
   | `Task ID` | Text | (free text, used to match BACKLOG.yaml tasks) |
   | `Status` | Single select | Proposed, Planning, Needs Decision, Ready, In Progress, Blocked, Dev Complete, QA Failed, QA Passed, Review Failed, Accepted, Done, Superseded |
   | `Milestone` | Single select or Iteration | Values matching ROADMAP.md milestones |
   | `Priority` | Single select | P0, P1, P2, P3 |
   | `Weight` | Number | 1-13 |
   | `Owner` | Text | GitHub username or role name |
   | `Dependencies` | Text | Comma-separated task IDs |
   | `Blocked by` | Text | Comma-separated task IDs |
   | `Docs Impact` | Single select | Pending, None, Resolved |

3. Set the repository variable `GH_PROJECT_NUMBER` to your project number (the numeric part of the project URL).
4. Set `GITHUB_TOKEN` (or `GH_TOKEN`) with `repo` and `project` scopes.
5. The workflow in `.github/workflows/sync-project.yml` runs automatically on push to `main`.

### Local token setup

Create a `.env` file in the repo root (listed in `.gitignore`, never committed):

```
GITHUB_TOKEN=ghp_your_fine_grained_token
GH_PROJECT_NUMBER=1
GH_OWNER=neitdung
```

The sync scripts and Makefile automatically load `.env` if present. Copy `.env.example` as a starting point.

## gh CLI workflow

Agents use **`gh` CLI commands** (via bash tool) to manage Issues and comments. The sync script (`scripts/harness/sync_issues.py`) translates between Issue state and GitHub Project custom fields + local harness files.

The `gh` CLI **cannot** set Project custom fields directly. The split is:

| Capability | Tool | Owner |
|------------|------|-------|
| Create/read Issues (task bodies) | `gh issue create`, `gh issue view` | Agent |
| Add handoff/QA/review comments | `gh issue comment` with `<!-- marker -->` | Agent |
| Set Status, Milestone, Priority, Owner fields | **sync script**: `make sync-push` | After agent edits |
| Create ADR | `gh issue create --label adr,decision` | Agent |
| Regenerate local files for validation | **sync script**: `make sync-pull` | After edits |

### Branch naming convention

Every implementation branch must use a descriptive prefix and follow this
pattern:

```text
<prefix>/<task-id>-<short-description>
```

Allowed prefixes:
| Prefix | Use case |
|--------|----------|
| `feat/` | New feature or enhancement |
| `fix/` | Bug fix or regression fix |
| `chore/` | Maintenance, tooling, config |
| `docs/` | Documentation only changes |
| `refactor/` | Code restructuring without behavior change |

Example: `feat/NH-HARNESS-002-branch-pr-workflow`

### gh CLI commands to use

| Action | Command |
|--------|---------|
| Create a task | `gh issue create --title "[NH-XXX-###] Title" --body "$(cat task.md)" --label task --repo neitdung/novelhub` |
| Read task packet | `gh issue view <number> --json body --jq .body --repo neitdung/novelhub` |
| Create/switch branch | `git checkout -b <prefix>/<task-id>-<description>` |
| Post handoff | `gh issue comment <number> --body "<!-- handoff -->\n\n$(cat handoff.md)" --repo neitdung/novelhub` |
| Create PR (Developer) | `gh pr create --title "[NH-XXX-###] Title" --body "Closes #<issue-num>" --base main` |
| Post QA report on PR | `gh pr comment <pr-number> --body "<!-- qa-report -->\n\n$(cat report.md)"` |
| Post review on PR | `gh pr review <pr-number> --approve --body "$(cat report.md)"` |
| Post review (changes req) | `gh pr review <pr-number> --request-changes --body "$(cat report.md)"` |
| Merge PR (Manager) | `gh pr merge <pr-number> --merge --subject "[NH-XXX-###] Title"` |
| Close Issue | `gh issue close <number> --repo neitdung/novelhub` |
| Create ADR | `gh issue create --title "[ADR-XXXX] Title" --body "$(cat adr.md)" --label adr,decision --repo neitdung/novelhub` |

### Required artifact flow

| State transition | Agent | Action |
|-----------------|-------|--------|
| `proposed` → `planning` | Manager | `gh issue create` with task packet as body, `task` label. Then sync: `make sync-push` to set Status→Planning. |
| `planning` → `ready` | Planner | `gh issue edit <num> --body "$(cat task.md)"`. Then sync: `make sync-push` to set Status→Ready. |
| `ready` → `in_progress` | Manager | Write task fields in BACKLOG.yaml, then `make sync-push` to set Status→In Progress, Owner. Suggest branch name with proper prefix (`feat/`, `fix/`, `chore/`, `docs/`, `refactor/`). |
| `in_progress` → `dev_complete` | Developer | Create/switch to branch (`git checkout -b <prefix>/<task-id>-<desc>`). Implement, test, commit, push. Create PR (`gh pr create`). `gh issue comment` with `<!-- handoff -->`. Write state change in BACKLOG.yaml. Sync: `make sync-push`. |
| `dev_complete` → `qa_passed` | QA | Check out the PR branch. Validate. `gh pr comment` with `<!-- qa-report -->`. Sync: `make sync-push`. |
| `qa_passed` → `accepted` | Reviewer | Review PR diff. `gh pr review` with `--approve` or `--request-changes`. Sync: `make sync-push`. |
| `accepted` → `done` | Manager | Merge PR (`gh pr merge`). Switch to main, pull latest, delete branch. Sync: `make sync-push` to set Status→Done, close Issue (`gh issue close`). |

### Simplified workflow

```text
1. Agent runs gh CLI commands to create/update Issues and comments
2. Agent updates local BACKLOG.yaml (state, owner, etc.)
3. Run make sync-push    → pushes state to GitHub Project fields
4. Run make sync-pull     → regenerates local files from Issues
5. Run make harness-check → validates everything
```

## Sync commands

```bash
# Pull Issues → local files (regenerates BACKLOG.yaml, task packets, handoffs, reports)
make sync-pull

# Push local files → Issues (bootstrap after setting up from backup)
make sync-push

# Both directions
make sync-project
```

Run `make sync-pull` before `make harness-check` to ensure local files reflect the current Issue state.

## Roles

The complete role descriptions, authority boundaries, required skills, inputs,
and outputs are in `.agents/AGENT_CATALOG.md`.

| Agent | Required skill |
|-------|----------------|
| Manager | `$manage-project` |
| Planner | `$plan-task` |
| Developer | `$implement-task` |
| QA | `$qa-task` |
| Reviewer | `$review-task` |
| Documentation | `$document-task` |

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

- `ready`: task packet exists (Issue body or local file).
- `dev_complete`: developer handoff exists (Issue comment with `<!-- handoff -->` or local file).
- `qa_passed`: passing QA report exists (Issue comment with `<!-- qa-report -->` or local file).
- `accepted`: approved review report exists (Issue comment with `<!-- review-report -->` or local file).
- `done`: all prior artifacts exist and documentation impact is resolved.

## Stable commands

```bash
make harness-check
make status
make status-write
make task-check ID=<task-id>
make sync-pull
make sync-push
make check
make integration
make e2e
make ci
```

Commands must be non-interactive and return non-zero on failure.
