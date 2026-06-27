# NovelHub Project Context

## Product

NovelHub is a privacy-first, local novel library, analysis pipeline, entity knowledge base, wiki, visualization suite, and cited chat interface.

## Supported languages

- Chinese
- Vietnamese
- English

The architecture must remain extensible to other languages. Translation is not part of the initial product.

## Technical baseline

- Frontend: React 19, TypeScript, Next.js (App Router, server mode with API proxy), Chakra UI.
- State: Redux Toolkit, React Redux, RTK Query.
- Backend: Python 3.11+, FastAPI async.
- Database: SQLite, aiosqlite, FTS5.
- Realtime: WebSocket with polling fallback.
- LLM: Ollama default; explicit OpenAI-compatible and Anthropic options.
- Test stack: Pytest, Vitest, React Testing Library, Playwright.

## Architecture constraints

- Local-first and no telemetry.
- Novel content is not sent externally without explicit cloud-provider configuration and user approval.
- Optimize prompts and extraction for a 16K context window.
- Wiki generation is on demand.
- Server-owned data stays in RTK Query; client-owned global state stays in Redux slices.
- Chakra UI is the sole UI component and theme system.
- Database migrations and backup/restore require data-safety tests.
- Merge gates use deterministic fake LLMs; live-provider tests are opt-in.

## Non-goals for MVP

- Automatic translation.
- Multi-user accounts and remote collaboration.
- Hosted SaaS deployment.
- Mobile-native applications.
- Arbitrary agent shell/database tools exposed through chat.

## Human approval requirements

- Product or architecture scope changes.
- Destructive or irreversible data operations.
- Paid/cloud dependencies or external content transmission.
- Secret-management policy changes.
- Breaking API/schema acceptance and releases.
