# NH-CHAT-002 — Chat Tools and Citations

## Objective
Implement chat tools for wiki search, entity lookup, and citation verification.

## Acceptance Criteria
1. Tool registry for wiki search, entity lookup, timeline
2. Citation verifier for source references
3. Tool execution with allowlist
4. Tests for tool execution and citation validation

## Verification
```bash
cd backend && .venv/bin/pytest tests/test_chat_tools.py -v
```

## Owned Paths
- `backend/app/chat/tools.py` (new module)
- `backend/app/chat/citations.py` (new module)
