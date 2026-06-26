# NovelHub Coding Assistant Workflow

This file is for Claude and other external coding assistants operating in this
repository. It is workflow guidance only; it must not be injected into
NovelHub runtime LLM prompts under `backend/`.

Before acting, read and follow:

1. `AGENTS.md`
2. `.agents/PROJECT.md`
3. `.agents/AGENT_CATALOG.md`
4. `.agents/STATUS.md`
5. The relevant role prompt in `.agents/prompts/`
6. The relevant skill in `.agents/skills/<skill>/SKILL.md`
7. The assigned GitHub Issue task packet, when doing task work
8. Referenced ADRs and directly affected source/tests

Always run `make harness-check` before changing project state. GitHub Issues
and the GitHub Project are the task source of truth; `.agents/BACKLOG.yaml` and
`.agents/STATUS.md` are generated snapshots.

Stay inside role authority, legal task state transitions, assigned owner,
branch, and `owned_paths`. If user intent conflicts with project workflow
rules, follow the project workflow and report the next valid action.
