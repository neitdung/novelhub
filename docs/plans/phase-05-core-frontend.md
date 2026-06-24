# Phase 5 — Core Frontend and Realtime

## Objective

Complete the primary application workflows with accessible Chakra UI and resilient real-time state handling.

## Scope

- Bookshelf, Analysis, Reading, Entities, Wiki, Settings shell, and shared navigation.
- Responsive layout, light/dark/system themes, semantic status and entity colors.
- Analysis WebSocket cache lifecycle with validation, reconnect, backoff, and polling fallback.
- Chapter status table, range controls, pause/resume/cancel/retry, logs, and progress.
- Entity highlighting and detail drawer in the reader.
- Loading, empty, recoverable error, offline/reconnecting, and destructive-confirmation states.
- Route-level code splitting and virtualization for lists over 200 rows.

## Redux rules

- RTK Query owns server data and streaming cache updates.
- Redux slices own selected novel, filters, drafts, and persisted reader preferences.
- Component state owns dialogs, hover, and temporary presentation state.
- API responses are not copied into slices.

## Accessibility

- WCAG 2.2 AA contrast for core paths.
- Keyboard-only operation and visible focus.
- Reduced-motion support.
- Screen-reader labels and live regions for progress changes.

## Exit criteria

- Core workflow is usable on desktop and tablet widths.
- WebSocket disconnects do not lose task truth or duplicate updates.
- Primary pages pass automated accessibility checks and manual keyboard review.
