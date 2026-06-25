# NH-HARD-001 — Security Hardening

## Objective
Add security measures: input validation, rate limiting, sanitization.

## Acceptance Criteria
1. Input validation for all API endpoints
2. Rate limiting middleware
3. Markdown sanitization
4. Security headers

## Verification
```bash
cd backend && .venv/bin/pytest tests/test_security.py -v
```

## Owned Paths
- `backend/app/security.py` (new module)
- `backend/app/middleware.py` (new module)
