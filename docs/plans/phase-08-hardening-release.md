# Phase 8 — Hardening and Release

## Objective

Prove production readiness for local use across supported languages and package the first release.

## Scope

- Full security, privacy, accessibility, performance, migration, and recovery review.
- Representative Chinese, Vietnamese, and English end-to-end datasets.
- Long-running analysis, cancellation, restart, disk-full, corrupt-data, and provider-outage tests.
- Dependency and license audit.
- Packaging/install strategy and first-run diagnostics.
- User guide, troubleshooting, backup guidance, and release notes.

## Release gates

- Harness, lint, type, unit, integration, E2E, accessibility, and migration suites pass.
- No open critical/high defects; accepted lower risks are documented.
- Fresh install and upgrade from previous supported version pass.
- Backup before upgrade and restore after upgrade are demonstrated.
- Privacy defaults and cloud disclosures are manually reviewed.
- Human approves release candidate.

## Exit criteria

- A non-developer can install, configure a local model, ingest a novel, analyze it, browse entities, generate a wiki, chat with citations, and restore a backup.
- Release artifacts are reproducible and checksummed.
- Known limitations and support boundaries are documented.
