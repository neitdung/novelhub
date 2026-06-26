# NovelHub Coding Assistant Workflow

This repository uses a project workflow harness. These instructions are for
coding assistant behavior only; do not apply them to NovelHub runtime LLM
prompts under `backend/`.

Before proposing or editing code, read `AGENTS.md`, `.agents/PROJECT.md`,
`.agents/AGENT_CATALOG.md`, `.agents/STATUS.md`, the relevant role prompt in
`.agents/prompts/`, the matching skill in `.agents/skills/`, the assigned
GitHub Issue task packet, referenced ADRs, and directly affected source/tests.

Run `make harness-check` before changing project state. Respect task state,
owner, branch, `owned_paths`, required artifacts, verification commands, and
privacy/data-safety rules.
