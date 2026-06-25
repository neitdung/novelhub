# NH-FE-002 — Theme System

## Objective
Implement light/dark/system theme support with persistence.

## Acceptance Criteria
1. Theme context with light, dark, and system modes
2. Theme toggle in header
3. Preference persisted in localStorage
4. Respects system preference on first load

## Verification
```bash
cd frontend && npx tsc --noEmit
```

## Owned Paths
- `frontend/src/context/ThemeContext.tsx` (new)
- `frontend/src/components/ThemeToggle.tsx` (new)
