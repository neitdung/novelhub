# NH-FOUND-001 — Scaffold backend and frontend toolchains

## Metadata

- Milestone: `foundation`
- Priority: P0
- Weight: 3
- Owner: unassigned
- Dependencies: `NH-HARNESS-001`
- Proposed owned paths: `backend/`, `frontend/`, root toolchain configuration
- ADRs: `ADR-0002`

## Problem and outcome

Create minimal runnable backend and frontend applications with stable quality commands. This task establishes toolchains only; feature APIs and database schema are separate tasks.

## In scope

- Python backend project and FastAPI health endpoint.
- React 19 + TypeScript + Vite frontend.
- Chakra UI provider and a minimal routed shell.
- Redux Toolkit store and RTK Query base API.
- Backend/frontend lint, type-check, and unit-test commands.
- Update root Make targets to invoke both projects.

## Out of scope

- Novel ingestion and database feature tables.
- LLM providers and WebSockets.
- Production packaging.

## Acceptance criteria

- [ ] Backend starts and typed `/api/health` returns success.
- [ ] Frontend starts and renders a Chakra UI application shell.
- [ ] Redux store and RTK Query middleware are configured.
- [ ] TypeScript strict mode is enabled.
- [ ] `make check` runs backend and frontend static/unit checks.
- [ ] Setup instructions work from a clean checkout.

## Verification commands

```bash
make check
```

## Package manager

Use npm with a committed `package-lock.json` as recorded in `ADR-0002`.

## Documentation impact

Pending.
