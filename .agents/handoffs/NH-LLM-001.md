# NH-LLM-001 Developer Handoff

## Summary
Implemented LLM provider interfaces for Ollama, OpenAI, Anthropic, and FakeLLM.

## Changes
- `backend/app/llm/base.py`: Abstract base class with LLMProvider, LLMConfig, LLMResponse
- `backend/app/llm/ollama.py`: Ollama provider implementation
- `backend/app/llm/openai.py`: OpenAI provider implementation
- `backend/app/llm/anthropic.py`: Anthropic provider implementation
- `backend/app/llm/fake.py`: Fake provider for testing
- `backend/tests/test_llm.py`: 5 tests covering all providers

## Verification
```bash
cd backend && .venv/bin/pytest tests/test_llm.py -v
cd backend && .venv/bin/ruff check app/llm/
cd backend && .venv/bin/mypy app/llm/
```

## Notes
- All providers implement the same interface
- FakeLLMProvider supports configurable responses and failure rates
- Usage tracking built into base class
