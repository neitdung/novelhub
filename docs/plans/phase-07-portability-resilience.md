# Phase 7 — Data Portability and Resilience

## Objective

Make user data portable, recoverable, and safe across upgrades.

## Scope

- Series-bible export to Markdown, Word, Excel, and PDF.
- Full backup ZIP with manifest, schema version, checksums, and application metadata.
- Restore preview, compatibility checks, conflict strategy, and transactional import.
- LLM/provider settings, health checks, hardware information, and model benchmark.
- Contradiction detection and wiki linting.
- Operational metrics and cloud cost estimates without telemetry.

## Data safety

- Restore never mutates the active database before validation succeeds.
- Create an automatic pre-restore backup.
- Reject path traversal, oversized archives, checksum mismatch, and unsupported schema versions.
- Secret values are excluded from backups and exports.
- Exported evidence preserves stable chapter references.

## Verification

- Round-trip backup tests from representative datasets.
- Restore failure injection at validation, extraction, migration, and swap stages.
- Previous-release backup compatibility fixture.
- Format-level smoke tests for all export types.

## Exit criteria

- Backup/restore round trips without data loss.
- Failed restore leaves the active database unchanged.
- Previous supported backup format upgrades successfully.
