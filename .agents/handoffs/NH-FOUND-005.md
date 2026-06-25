# NH-FOUND-005 — Developer Handoff

## Summary

Created OpenAPI contract export from FastAPI and contract validation script with Make targets.

## Changed paths

- `scripts/contracts/export_openapi.py` — Export OpenAPI spec from FastAPI
- `scripts/contracts/check_contract.py` — Validate OpenAPI spec
- `contracts/openapi.json` — Generated OpenAPI spec
- `Makefile` — Added contract-export, contract-check, contract-validate targets

## Acceptance criteria evidence

- [x] OpenAPI spec is exported from FastAPI
- [x] Frontend types can be validated against OpenAPI
- [x] Contract drift detection script works
- [x] `make check` includes contract validation

## Verification

| Command | Result | Notes |
|---------|--------|-------|
| `make contract-validate` | PASS | Exports and validates spec |
| `make check` | PASS | Full suite passes |

## Migrations and compatibility

No database changes. Contract validation is additive.

## Risks and follow-up

- No frontend type generation yet (deferred to when API grows)
- Contract check is basic validation (can be enhanced later)

## Suggested QA scenarios

1. Run `make contract-validate` and verify spec is exported
2. Run `make check` and verify contract validation passes
3. Verify `contracts/openapi.json` contains valid OpenAPI
