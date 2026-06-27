# NH-TOOL-002: Add Unified `install` Command

## Metadata

- **Task ID:** NH-TOOL-002
- **Title:** Add Unified `install` Command
- **Milestone:** `foundation`
- **Priority:** P2
- **Weight:** 3
- **Owner:** (to be assigned)
- **Dependencies:** NH-TOOL-001 (preferred — reduces merge conflicts on `Makefile` reorganization)
- **Proposed owned paths:** `Makefile`, `scripts/install.sh`
- **ADRs:** None

## Outcome

A single `make install` command installs all project dependencies — backend Python virtual environment, frontend npm packages, and harness/dev tooling — in one invocation. A corresponding `scripts/install.sh` script handles the actual installation so it can also be invoked directly.

## In scope

- **Create `scripts/install.sh`** that:
  - Installs backend dependencies via `cd backend && uv sync` (matching current `backend-install`).
  - Installs frontend dependencies via `cd frontend && npm ci` (matching current `frontend-install`).
  - Installs harness dependencies: creates backend `.venv` if needed, ensures `pip` is available, installs any dev extras required for harness scripts (if any).
  - Is idempotent — safe to run multiple times.
  - Respects existing `.venv` and `node_modules` (does not destroy them unless forced).
  - Supports environment variables via `.env` loading.
  - Has a `--help` flag documenting usage.
- **Add `make install` target** at the **top** of the `Makefile` (before all other targets) that calls `scripts/install.sh`.
- **Update `scripts/start.sh`** — the `INSTALL_DEPS=1` flow currently has inline dependency install logic. If NH-TOOL-001 runs first, refactor `start.sh` to delegate to `scripts/install.sh` instead of duplicating install logic. (If NH-TOOL-001 hasn't run, keep `start.sh` as-is but note the duplication risk.)

## Out of scope

- Adding any Gem, system package manager (apt, brew), or OS-level dependency installation.
- Installing Ollama or any LLM runtime.
- Modifying harness scripts (`scripts/harness/`).
- Adding any CI pipeline changes.
- Modifying `backend/pyproject.toml` or `frontend/package.json` dependency lists.

## Implementation constraints

- The install script must be a standalone bash script (not inline Make).
- Must not assume a pre-existing `.venv` — it should create one if absent.
- Must handle the case where `uv` is not available (fallback to `pip`).
- Must exit non-zero if any installation step fails.
- Must be compatible with `set -e` (fail-fast by default).
- Must load `.env` if present (like `start.sh` does).

## Acceptance criteria

1. **`scripts/install.sh` exists** and is executable (`chmod +x`).
2. **`make install` works**: running `make install` from a clean checkout creates `.venv` in `backend/`, installs all Python deps, runs `npm ci` in `frontend/`, and exits 0.
3. **Idempotency**: Running `make install` twice on an already-installed project exits 0 and does not re-download everything unnecessarily.
4. **`make install --help`** or `scripts/install.sh --help` prints usage information.
5. **Failure handling**: If `uv sync` fails, the script exits non-zero.
6. **No regressions**: `make backend-install` and `make frontend-install` still work independently.
7. **No dead code**: If `start.sh` is updated to delegate to `install.sh`, the old inline install blocks are removed.

## Verification commands

```bash
make harness-check
make install
# Verify backend .venv exists
test -d backend/.venv
test -f backend/.venv/bin/python
# Verify frontend node_modules exists
test -d frontend/node_modules
# Verify it's idempotent
make install
# Verify independent targets still work
make backend-install
make frontend-install
```

## Security, privacy, and data safety

No novel data is touched. The script may download packages from PyPI and npm registries (standard open-source package management).

## Compatibility and rollback

No data migration. Rollback by removing `scripts/install.sh` and reverting the `Makefile` and `start.sh` changes.

## Documentation impact

`pending` — the new `make install` command should be documented in developer setup instructions. The current `AGENTS.md` "stable commands" list should be checked; if the user expects `make install` to be a standard setup step, it should be listed. Also update `README.md` or any quick-start docs if they exist.

## Assumptions and open questions

- `uv` is expected to be available on the developer's system (it already is for `make backend-install`).
- If `uv` is not found, the script could fall back to `pip install -e .` but this is not required by acceptance criteria — current behavior uses `uv`.
- Should `install.sh` also install the `dev` extras from `pyproject.toml`? (Current `uv sync` does, so yes by delegation.)
- The `start.sh` delegation optimization is optional and carries a dependency on NH-TOOL-001.

## Completion evidence

- `scripts/install.sh` created and executable.
- `make install` target added to `Makefile` at the top.
- All verification commands pass.
