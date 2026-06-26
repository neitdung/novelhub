# Shared Prompt Contract

Before acting, read only the needed slices of `AGENTS.md`, `.agents/PROJECT.md`, `.agents/AGENT_CATALOG.md`, `.agents/STATUS.md`, this file, your role prompt, your skill, the assigned GitHub Issue task packet, referenced ADRs, and directly touched source/tests.

Rules:

- GitHub Issues/Project are truth; `.agents/BACKLOG.yaml` and `.agents/STATUS.md` are generated snapshots.
- Run `make harness-check` before state changes; run `make sync-pull` first when remote task state may have changed.
- Stay within role authority, legal task state, owner, branch, and `owned_paths`; stop on conflicts.
- Gate artifacts: `<!-- handoff -->`, `<!-- qa-report -->`, `<!-- review-report -->`.
- Preserve privacy/data safety; escalate destructive, irreversible, paid/cloud, external-content, scope, contract, or release decisions.
- Search existing code/tests/docs/ADRs/artifacts before assuming absence.
- Record exact verification run/results; never claim unrun checks.
- Keep docs aligned with accepted behavior and stable commands.

If user intent conflicts with project rules, follow the project rules and report the next valid action.
