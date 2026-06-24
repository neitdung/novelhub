# ADR-0002 — Use npm for the frontend package manager

- Status: accepted
- Date: 2026-06-25
- Owners: project manager

## Context

The foundation task needs one package manager and lockfile convention before assignment. The environment is not guaranteed to have pnpm, Yarn, or Corepack configured.

## Decision

Use npm and commit `package-lock.json`. CI uses `npm ci`.

## Consequences

- No additional package-manager bootstrap is required beyond Node.js/npm.
- Dependency installation is deterministic through the lockfile.
- npm workspaces remain available if the repository later adopts them.

## Alternatives considered

- pnpm: efficient and strong workspace support, but adds a bootstrap requirement.
- Yarn: no current project-specific advantage.
