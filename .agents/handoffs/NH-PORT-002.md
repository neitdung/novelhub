# Developer Handoff: NH-PORT-002

## Summary
Implemented backup ZIP with manifest/checksum, restore with validation.

## Files Changed
- backend/app/backup.py
- backend/app/routers/backup.py
- backend/tests/test_backup.py

## Implementation Details
- create_backup: ZIP with manifest.json + novelhub.db
- validate_backup: Schema version, checksum validation
- restore_backup: Backup current DB, extract and replace
- API endpoints: /api/backup, /api/backup/validate, /api/backup/restore

## Verification
- All tests pass: `cd backend && pytest tests/test_backup.py -v`
- Lint clean
- Type check clean
