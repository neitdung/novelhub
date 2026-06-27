# NH-TOOL-003: Add `start`, `stop`, `clear` Commands at the Top of Makefile

## Metadata

- **Task ID:** NH-TOOL-003
- **Title:** Add `start`, `stop`, `clear` Commands at the Top of Makefile
- **Milestone:** `foundation`
- **Priority:** P2
- **Weight:** 2
- **Owner:** (to be assigned)
- **Dependencies:** NH-TOOL-001 (preferred — reduces merge conflicts on `Makefile` reorganization)
- **Proposed owned paths:** `Makefile`
- **ADRs:** None

## Outcome

Three intuitive Makefile targets are added at the **top** of the `Makefile` (before all other targets) to provide simple, memorable entry points for common development tasks:

| Target | Action |
|--------|--------|
| `make start` | Delegates to `scripts/start.sh`; supports passing flags like `--local` |
| `make stop`  | Delegates to `scripts/stop.sh`; stops all running services |
| `make clear` | Delegates to `scripts/clear_data.sh`; clears data and caches |

These targets are `.PHONY`, clearly documented with comments, and behave identically to running the scripts directly.

## In scope

- **Add `make start` target** at the top of the `Makefile` that:
  - Calls `scripts/start.sh`.
  - Passes optional flags from the command line, e.g., `make start --local` should pass `--local` to `start.sh`.
  - Approach: Use `MAKEFLAGS` or a variable like `ARGS` to forward extra arguments.
    ```makefile
    start:
        ./scripts/start.sh $(ARGS)
    ```
    Usage: `make start ARGS="--local"` or more ergonomically `make start --local` (GNU Make passes unknown flags as `MAKEFLAGS`, not as positional args). The recommended pattern is:
    ```makefile
    start:
        ./scripts/start.sh
    ```
    If users need `--local`, they can call `make start ARGS=--local` or `./scripts/start.sh --local`.
- **Add `make stop` target** that calls `scripts/stop.sh`.
- **Add `make clear` target** that calls `scripts/clear_data.sh`.
- **Add `.PHONY` declarations** for `start`, `stop`, `clear` in the existing `.PHONY` line.
- **Place these three targets at the top** of the `Makefile` (immediately after the `.PHONY` line), above all other targets, so they are the first thing a developer sees when running `make` or reading the file.
- **Add a section comment** like `# === Developer quick-start commands ===` above the block.

## Out of scope

- Modifying `scripts/start.sh`, `scripts/stop.sh`, or `scripts/clear_data.sh` in any way (behavior changes are covered by NH-TOOL-001).
- Adding interactive prompts or TUI elements.
- Adding any other `make` targets.
- Changing the harness, backend, frontend, or CI workflows.

## Implementation constraints

- Must use the existing scripts as-is — no wrapper scripts.
- Targets must be `.PHONY`.
- Must be placed at the top of the Makefile (after variable declarations and `.PHONY` but before other sections).
- Must pass flags through to scripts (use `$(filter-out --,$(MAKEFLAGS))` if attempting to forward flags, or document the `ARGS=...` pattern).
- Must not break any existing Makefile syntax.

## Acceptance criteria

1. **`make start` works**: Runs `scripts/start.sh` and the server starts normally.
2. **`make stop` works**: Runs `scripts/stop.sh` and stops running services.
3. **`make clear` works**: Runs `scripts/clear_data.sh` and clears data.
4. **Flag forwarding**: `make start ARGS=--local` passes `--local` to `start.sh`.
5. **Placement**: The three targets appear at the top of the `Makefile`, immediately after variable declarations and `.PHONY`.
6. **`.PHONY` updated**: `start`, `stop`, `clear` are declared `.PHONY`.
7. **No regressions**: All existing targets (`make harness-check`, `make backend-check`, `make frontend-check`, `make check`, `make sync-*`, etc.) still work.

## Verification commands

```bash
make harness-check
# Verify the targets exist and are at the top
head -20 Makefile | grep -q "start"
head -20 Makefile | grep -q "stop"
head -20 Makefile | grep -q "clear"
# Verify they are .PHONY
grep -q "start" Makefile | head -1
# Actually test the targets (note: start needs the environment to be set up)
make stop   # Should succeed (services may or may not be running)
# Verify other targets still work
make backend-check
make frontend-check
```

## Security, privacy, and data safety

`make clear` destroys the local SQLite database file — this is intentional and matches the existing `clear_data.sh` behavior. Users should be aware that this is destructive to local data.

## Compatibility and rollback

No data migration. Rollback by reverting Makefile changes.

## Documentation impact

`pending` — these commands should be documented in developer setup instructions. `make start`, `make stop`, `make clear` should be added to `AGENTS.md` stable commands table if they are intended as standard developer entry points.

## Assumptions and open questions

- Flag forwarding via `ARGS=...` is the simplest and most compatible approach. GNU Make does not support passing unhandled flags as positional arguments to targets in a portable way. The documentation should show `make start ARGS=--local` as the usage.
- `make start` is expected to be run from the project root (this is already the convention for all Makefile targets).
- These targets should appear **before** other targets so they are the first thing developers see — this is a deliberate DX choice.

## Completion evidence

- Three new Makefile targets (`start`, `stop`, `clear`) at the top of the file.
- `.PHONY` declaration updated.
- All existing targets still work.
