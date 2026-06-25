# NH-FOUND-001 — Developer Handoff

## Summary

Scaffolded backend (Python FastAPI) and frontend (React 19 + TypeScript + Vite) with health endpoint, Chakra UI, Redux Toolkit, RTK Query, and all quality tooling.

## Changed paths

- `backend/` — FastAPI project with health endpoint, config, tests
- `frontend/` — React 19 + TypeScript + Vite with Chakra UI, Redux, RTK Query
- `Makefile` — Updated with backend and frontend commands

## Acceptance criteria evidence

- [x] Backend starts and typed `/api/health` returns success
- [x] Frontend starts and renders a Chakra UI application shell
- [x] Redux store and RTK Query middleware are configured
- [x] TypeScript strict mode is enabled
- [x] `make check` runs backend and frontend static/unit checks
- [x] Setup instructions work from a clean checkout

## Verification

| Command | Result | Notes |
|---------|--------|-------|
| `make harness-check` | PASS | Harness validation passed |
| `make backend-check` | PASS | ruff, mypy, pytest all pass |
| `make frontend-check` | PASS | oxlint, tsc, vitest all pass |
| `make check` | PASS | Full check suite passes |

## Migrations and compatibility

No database migrations. Backend uses SQLite via aiosqlite (not yet connected). Frontend uses npm with committed package-lock.json per ADR-0002.

## Risks and follow-up

- Backend config is minimal; database connection will be added in NH-FOUND-003
- Frontend uses basic Vite dev server; production proxy/serve configuration is deferred
- No environment validation beyond defaults yet

## Suggested QA scenarios

1. Verify `make backend-test` passes (2 tests)
2. Verify `make frontend-test` passes (8 tests)
3. Verify `make check` passes end-to-end
4. Manual: `cd backend && .venv/bin/uvicorn app.main:app` then `curl http://localhost:8000/api/health`
