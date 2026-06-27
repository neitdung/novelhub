# NH-TOOL-002 Developer Handoff

## Summary

Added a unified `install` command for the project:

1. **Created `scripts/install.sh`**: Standalone bash script that installs all project dependencies:
   - Backend Python deps via `uv sync`
   - Frontend npm packages via `npm ci`
   - Loads `.env` if present
   - `--help` flag for usage
   - Idempotent (safe to run multiple times)
   - Exits non-zero on failure

2. **Added `make install` target** at the top of Makefile (delegates to `scripts/install.sh`).

3. **Added developer quick-start targets** at the top of Makefile:
   - `make start` — runs `scripts/start.sh`
   - `make start ARGS=--local` — passes `--local` flag
   - `make stop` — runs `scripts/stop.sh`
   - `make clear` — runs `scripts/clear_data.sh`

## Verification

```bash
make harness-check                       # Passed
scripts/install.sh --help                # Prints usage
make -n install                          # ./scripts/install.sh
make -n start                            # ./scripts/start.sh 
make -n start ARGS=--local               # ./scripts/start.sh --local
make -n stop                             # ./scripts/stop.sh
make -n clear                            # ./scripts/clear_data.sh
make -n backend-check                    # Still resolves
make -n frontend-check                   # Still resolves
```

## Changed paths

| File | Change |
|------|--------|
| `scripts/install.sh` | **New** — unified dependency installer |
| `Makefile` | Added `install`, `start`, `stop`, `clear` targets at top; updated `.PHONY` |

## Risks

- `scripts/install.sh` requires `uv` to be available (same as `make backend-install`).
- `start.sh` still has inline dependency logic for `INSTALL_DEPS=1` path; could be refactored in future to delegate to `install.sh`.

## Handoff

**Verdict:** Ready for QA.

PR: https://github.com/neitdung/novelhub/pull/34
