# Phase 1 — Foundation and Contracts

## Objective

Create runnable backend and frontend shells with shared contracts, configuration, database migration infrastructure, and baseline quality tooling.

## Scope

### Backend

- Python 3.11+ project with FastAPI lifespan and structured configuration.
- SQLite connection management, WAL mode, foreign keys, migration runner, and health checks.
- Pydantic request/response/error envelopes.
- Logging with correlation IDs and secret redaction.
- Test application factory and temporary-database fixtures.

### Frontend

- React 19, TypeScript strict mode, Next.js (App Router, server mode with API proxy), Chakra UI provider and semantic tokens.
- Next.js App Router file-system routes (replacing React Router).
- Redux Toolkit store, typed hooks, RTK Query base API, normalized errors.
- Environment validation and error boundary.
- Vitest and React Testing Library setup.

### Contracts

- OpenAPI is the backend contract source.
- Generate or validate frontend API types from OpenAPI.
- Establish error codes, pagination, timestamps, identifiers, and WebSocket envelope conventions.

## Initial tasks

- `NH-FOUND-001`: Repository and toolchain scaffold.
- `NH-FOUND-002`: Backend app/config/health skeleton.
- `NH-FOUND-003`: SQLite migration baseline.
- `NH-FOUND-004`: Frontend Chakra/Redux/Router skeleton.
- `NH-FOUND-005`: OpenAPI contract and generated type check.

## Verification

- Backend starts and `/api/health` returns a typed response.
- Frontend starts and renders routed Chakra UI shell.
- Empty database migrates to the current schema.
- Frontend and backend contract check detects drift.
- Lint, type-check, and unit test commands are wired into `make check`.

## Exit criteria

- Clean checkout bootstraps with documented commands.
- No feature code bypasses configuration, error, or migration conventions.
- CI runs harness, backend, frontend, and contract checks.
