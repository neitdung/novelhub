# NH-CHAT-001 — Chat CRUD and Messages

## Objective
Implement chat conversations with persisted messages and streaming responses.

## Acceptance Criteria
1. Chat CRUD API: create, list, get, delete conversations
2. Message API: add message, list messages
3. Database migration for chat tables
4. All tests pass

## Verification
```bash
cd backend && .venv/bin/pytest tests/test_chat.py -v
```

## Owned Paths
- `backend/app/chat/` (new module)
- `backend/app/migrations.py` (add migration v3)
- `backend/app/routers/chat.py` (new router)
