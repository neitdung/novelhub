# NH-FE-003 — Settings Page and Enhanced Navigation

## Objective
Create settings page shell and enhance navigation with user preferences.

## Acceptance Criteria
1. Settings page with LLM provider selection
2. Enhanced navigation with breadcrumbs
3. Loading/error states for all pages
4. Empty states with helpful messages

## Verification
```bash
cd frontend && npx tsc --noEmit
```

## Owned Paths
- `frontend/src/pages/Settings.tsx` (new)
- `frontend/src/components/Breadcrumbs.tsx` (new)
- `frontend/src/components/LoadingState.tsx` (new)
- `frontend/src/components/ErrorState.tsx` (new)
- `frontend/src/components/EmptyState.tsx` (new)
