# NH-PORT-002 — Backup and Restore

## Objective
Implement full backup ZIP and restore with validation.

## Acceptance Criteria
1. Backup API: create backup ZIP with manifest
2. Restore API: validate and restore from backup
3. Schema version compatibility check
4. Tests for backup/restore round-trip

## Verification
```bash
cd backend && .venv/bin/pytest tests/test_backup.py -v
```

## Owned Paths
- `backend/app/backup.py` (new module)
- `backend/app/routers/backup.py` (new router)
