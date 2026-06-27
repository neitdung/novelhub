# NH-TOOL-001: Clean Up Makefile and scripts/ Directory

## Metadata

- **Task ID:** NH-TOOL-001
- **Title:** Clean Up Makefile and scripts/ Directory
- **Milestone:** `foundation`
- **Priority:** P2
- **Weight:** 3
- **Owner:** (to be assigned)
- **Dependencies:** None
- **Proposed owned paths:** `Makefile`, `scripts/`
- **ADRs:** None

## Outcome

The `scripts/` directory is logically reorganized, machine-specific scripts are moved to a dedicated subdirectory, and the `Makefile` is cleaned up with well-organized sections and clear comments — all without changing any script behavior.

## In scope

- **Reorganize `scripts/` directory:**
  - Move `local_llm.sh` and `remove_local_llm.sh` into a new subdirectory `scripts/local/` (these are machine-specific — they depend on local paths like `/home/bloot/tools/llama.cpp` and ROCm GPU detection).
  - Leave `start.sh`, `stop.sh`, `clear_data.sh` at the top level of `scripts/` (these are project-generic).
  - Leave `scripts/harness/` and `scripts/contracts/` untouched.
- **Update `start.sh`** to reference `scripts/local/local_llm.sh` instead of `scripts/local_llm.sh` (line 93, 100, 122).
- **Update `remove_local_llm.sh`** — keep it in `scripts/local/` but may also be referenced by other cleanup workflows. No code changes needed beyond the move.
- **Reorganize the `Makefile`** so targets are grouped into clear labelled sections with consistent comments:
  - Harness/management commands (bootstrap, harness-check, status, sync, task-check).
  - Backend commands (backend-install, backend-lint, etc.).
  - Frontend commands (frontend-install, frontend-lint, etc.).
  - Contract commands (contract-export, contract-check, etc.).
  - CI/composite commands (check, integration, e2e, ci).
  - `.PHONY` declarations kept at top, updated to include all targets.
  - Add white-space separation and section-header comments.
- **Remove dead or unused sections** — audit Makefile targets for anything stale.

## Out of scope

- Changing behavior or semantics of any script.
- Modifying scripts inside `scripts/harness/` or `scripts/contracts/`.
- Modifying the harness state machine or sync scripts.
- Adding new Makefile targets (covered by NH-TOOL-002 and NH-TOOL-003).
- Changing the `backend/` or `frontend/` source code.
- Adding or modifying tests.
- Changing the CI workflow in `.github/workflows/`.

## Implementation constraints

- All scripts must remain executable (`chmod +x`).
- References to moved scripts (e.g., `local_llm.sh` from `start.sh` and `remove_local_llm.sh`) must be updated to the new path.
- The `Makefile` must remain valid GNU Make syntax (no tabs vs spaces issues).
- No functional changes to any script logic.
- Do not modify the `.opencode/` instructions.

## Acceptance criteria

1. **Machine-specific scripts moved**: `scripts/local_llm.sh` and `scripts/remove_local_llm.sh` exist under `scripts/local/` and are removed from `scripts/`.
2. **start.sh references updated**: `start.sh` refers to `scripts/local/local_llm.sh` instead of `scripts/local_llm.sh`.
3. **Top-level scripts unchanged**: `start.sh`, `stop.sh`, `clear_data.sh` remain at `scripts/` root and are functionally identical.
4. **Makefile sections reorganized**: All Makefile targets are grouped into labelled sections (harness, backend, frontend, contracts, CI).
5. **Makefile .PHONY up to date**: All targets appear in the `.PHONY` declaration.
6. **All existing `make` targets still work**: `make harness-check`, `make backend-check`, `make frontend-check`, `make check`, `make sync-pull`, `make sync-push`, etc. all succeed.
7. **`git diff --stat` shows no changes outside owned paths** (only `Makefile` and `scripts/`).

## Verification commands

```bash
make harness-check
# Verify scripts/local/ exists and contains the moved scripts
test -f scripts/local/local_llm.sh
test -f scripts/local/remove_local_llm.sh
# Verify original locations are gone
test ! -f scripts/local_llm.sh
test ! -f scripts/remove_local_llm.sh
# Verify start.sh references the new path
grep -q "scripts/local/local_llm.sh" scripts/start.sh
# Verify all Makefile targets work
make backend-check
make frontend-check
make sync-pull
make sync-push
```

## Security, privacy, and data safety

No data is handled. This is purely a file reorganization and Makefile cleanup.

## Compatibility and rollback

No data migration. Rollback by reverting moved files:
```bash
git checkout main -- Makefile scripts/
```

## Documentation impact

`none` — no user-facing or developer docs reference absolute paths to moved scripts. The Makefile targets (which are documented in AGENTS.md and developer prompts) remain name-stable.

## Assumptions and open questions

- `local_llm.sh` and `remove_local_llm.sh` are genuinely machine-specific (they hardcode paths like `/home/bloot/tools/llama.cpp` and use ROCm-specific detection). Moving them to `scripts/local/` makes this clear.
- No other files in the repo reference `scripts/local_llm.sh` or `scripts/remove_local_llm.sh` beyond `start.sh`. (Should be verified during implementation.)
- `scripts/harness/` and `scripts/contracts/` are shared, cross-machine tooling and should not be moved.

## Completion evidence

- Moved script files land in `scripts/local/`.
- `start.sh` updated to reference new paths.
- `Makefile` has clear labelled sections.
- All `make` targets pass.
