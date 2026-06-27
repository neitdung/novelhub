# NH-TOOL-004: Fix `make install` and `make start` Commands

## Metadata

- **Task ID:** NH-TOOL-004
- **Title:** Fix `make install` and `make start` Commands
- **Milestone:** `foundation`
- **Priority:** P1
- **Weight:** 2
- **Owner:** (to be assigned)
- **Dependencies:** None
- **Proposed owned paths:** `backend/pyproject.toml`, `scripts/start.sh`
- **ADRs:** None

## Outcome

Both `make install` and `make start` succeed without errors, restoring the developer quick-start workflow.

- `make install` installs all backend Python dependencies (via `uv sync`) and frontend npm packages (via `npm ci`).
- `make start` launches the FastAPI backend server on the configured port (default 8000).

## In scope

### Fix 1: `backend/pyproject.toml` — configure setuptools package discovery

Add `[tool.setuptools.packages.find]` to resolve the "Multiple top-level packages discovered in a flat-layout" error:

```toml
[tool.setuptools.packages.find]
include = ["app*"]
exclude = ["uploads*", "tests*"]
```

This tells setuptools to only discover the `app` package (and any subpackages) while ignoring `uploads/`, `tests/`, and other non-package directories.

### Fix 2: `scripts/start.sh` — resolve `$PYTHON` as an absolute path

- After the initial `cd "$(dirname "$0")/.."` to the project root, resolve `PROJECT_ROOT` as an absolute path.
- Use `PROJECT_ROOT` to make all subsequent path references (`PYTHON`, `BACKEND_DIR`) absolute instead of relative.
- This fixes the bug where `cd "${BACKEND_DIR}"` then running `"$PYTHON"` fails because `$PYTHON` is a relative path from the project root, not from inside `backend/`.

Specifically:

```bash
# After cd "$(dirname "$0")/..", add:
PROJECT_ROOT=$(pwd)

# Change
PYTHON=${PYTHON:-${BACKEND_DIR}/.venv/bin/python}
# To
PYTHON=${PYTHON:-${PROJECT_ROOT}/${BACKEND_DIR}/.venv/bin/python}
```

## Out of scope

- Changing the `Makefile` targets themselves (they delegate correctly to the scripts).
- Modifying `frontend/` dependency installation (npm ci already works).
- Adding new features to the start/install scripts.
- Modifying any other scripts (`stop.sh`, `clear_data.sh`).
- Changing the existing backend/frontend toolchain commands (`make backend-install`, `make frontend-install`).

## Implementation constraints

- The fix must be minimal — only the lines needed to resolve the two root causes.
- Must not break any existing Makefile targets or other scripts.
- Must preserve backward compatibility: `$PYTHON` and `$BACKEND_DIR` environment variable overrides must still work.
- Must not require manual steps beyond `make install && make start`.

## Acceptance criteria

1. **`make install` succeeds**: Runs `uv sync` in `backend/` and `npm ci` in `frontend/` without errors.
2. **`make start` succeeds**: Launches the FastAPI backend on `http://127.0.0.1:8000` and the health endpoint responds.
3. **Backend deps installed**: `backend/.venv/bin/python -c "import fastapi"` returns successfully after `make install`.
4. **Setuptools package discovery**: `cd backend && uv pip list` includes `novelhub-backend` as installed in editable mode.
5. **Env var override works**: `PYTHON=/custom/python make start` still uses the custom Python path.
6. **No regressions**: `make harness-check`, `make backend-check`, `make frontend-check`, and `make check` still pass.

## Verification commands

```bash
# Verify the install works
make install

# Verify backend package is installed
backend/.venv/bin/python -c "import fastapi; print(fastapi.__version__)"

# Verify start works (run in background, check health, then stop)
make start &
sleep 5
curl -sf http://127.0.0.1:8000/api/health && echo "HEALTH OK"
make stop

# Verify harness still passes
make harness-check

# Verify env var override
PYTHON=$(pwd)/backend/.venv/bin/python make start &
sleep 3
curl -sf http://127.0.0.1:8000/api/health && echo "HEALTH OK"
make stop
```

## Security, privacy, and data safety

No novel content or credentials are involved. The fix only touches build configuration and the start script's working-directory logic.

## Compatibility and rollback

No data migration. Rollback by reverting changes to `backend/pyproject.toml` and `scripts/start.sh`.

## Documentation impact

`none` — the existing `make install` and `make start` usage instructions are unchanged; this fix makes them actually work.

## Assumptions and open questions

- The `make install` failure is 100% reproducible (newer setuptools versions) and has no workaround beyond the config fix.
- The start script relative-path bug is deterministic and occurs whenever `.venv/bin/python` is accessed after `cd backend`.
- The fix preserves the ability to override `$PYTHON` with an env var; if the user provides a relative path it's their responsibility.

## Completion evidence

- `backend/pyproject.toml` has a new `[tool.setuptools.packages.find]` section.
- `scripts/start.sh` resolves `$PYTHON` to an absolute path from `$PROJECT_ROOT`.
- Both `make install` and `make start` exit 0 and produce expected output.
