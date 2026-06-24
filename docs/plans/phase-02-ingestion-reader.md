# Phase 2 — Novel Ingestion and Reader

## Objective

Deliver a local novel library: upload, parse, review chapters, read content, persist progress, and manage bookmarks.

## Scope

- Upload `.txt` and `.md` with size, encoding, extension, and duplicate-hash validation.
- Detect Chinese, Vietnamese, and English source language.
- Split chapters with configurable patterns and a safe fallback.
- Preview and correct title, author, language, and chapter boundaries before commit.
- Novel/chapter CRUD, exclusion flags, reading state, and bookmarks.
- Bookshelf and reader pages using Chakra UI.
- RTK Query cache tags for novels, chapters, state, and bookmarks.
- Reader preferences in a small persisted Redux allowlist.

## Data work

- `novels`, `chapters`, `user_state`, and `bookmarks`.
- Store source file hash and parsing metadata.
- Preserve original text; normalization is derived, not destructive.

## Edge cases

- UTF-8 BOM, CRLF, very long lines, no chapter headings, duplicate chapter titles.
- Empty chapters, mixed-language metadata, interrupted upload, duplicate files.
- Deleting a novel must report affected data and require confirmation.

## Verification

- Golden parser fixtures for all target languages.
- API tests for upload, duplicate detection, CRUD, bookmarks, and delete cascade.
- UI tests for upload preview, reader navigation, keyboard behavior, and persistence.
- E2E: upload fixture → confirm chapters → open reader → bookmark → reload.

## Exit criteria

- A user can reliably ingest and read representative novels without an LLM.
- Restart preserves library, progress, bookmarks, theme, and reader settings.
- No original source content is silently modified.
