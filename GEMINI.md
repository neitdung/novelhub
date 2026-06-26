# NovelHub Coding Assistant Workflow

This file is for Gemini and other external coding assistants operating in this
repository. It is workflow guidance only; it must not be injected into
NovelHub runtime LLM prompts under `backend/`.

Use `AGENTS.md` as the authoritative instruction file, then read
`.agents/PROJECT.md`, `.agents/AGENT_CATALOG.md`, `.agents/STATUS.md`, the
required role prompt in `.agents/prompts/`, the required skill in
`.agents/skills/`, assigned GitHub Issue task packet, referenced ADRs, and
directly affected source/tests before acting.

Run `make harness-check` before changing project state. Follow the harness
state machine, ownership boundaries, artifact requirements, privacy rules, and
verification requirements from `AGENTS.md` and `.agents/prompts/common.md`.
