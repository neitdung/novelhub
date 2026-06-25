# NH-FOUND-005 — OpenAPI contract and generated type check

## Metadata

- Milestone: `foundation`
- Priority: P0
- Weight: 2
- Owner: unassigned
- Dependencies: `NH-FOUND-001`
- Proposed owned paths: `backend/`, `frontend/`, `contracts/`
- ADRs: none

## Problem and outcome

Establish OpenAPI as the backend contract source and validate frontend API types against it. Create a contract check that detects drift between backend and frontend.

## In scope

- Export OpenAPI spec from FastAPI
- Generate or validate frontend API types from OpenAPI
- Contract drift detection script
- Make target for contract validation

## Out of scope

- Full API implementation beyond health endpoint
- WebSocket contract
- Complex type generation

## Acceptance criteria

- [ ] OpenAPI spec is exported from FastAPI
- [ ] Frontend types can be validated against OpenAPI
- [ ] Contract drift detection script works
- [ ] `make check` includes contract validation

## Verification commands

```bash
make check
```

## Documentation impact

Pending.
