# NH-FE-001 — WebSocket Analysis Progress

## Objective
Add WebSocket support for real-time analysis progress updates.

## Acceptance Criteria
1. Backend WebSocket endpoint at `/ws/analysis/{novel_id}`
2. Frontend WebSocket connection with reconnection logic
3. Progress updates pushed to Redux store
4. Connection status indicator in UI

## Verification
```bash
cd backend && .venv/bin/pytest tests/test_ws.py -v
cd frontend && npx tsc --noEmit
```

## Owned Paths
- `backend/app/ws.py` (new module)
- `frontend/src/hooks/useWebSocket.ts` (new hook)
- `frontend/src/store/slices/analysisSlice.ts` (new slice)
