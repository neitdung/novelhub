from __future__ import annotations

from .anthropic import AnthropicProvider
from .base import LLMConfig, LLMProvider, LLMResponse
from .fake import FakeLLMProvider
from .local import LocalLLMProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider

__all__ = [
    "AnthropicProvider",
    "FakeLLMProvider",
    "LLMConfig",
    "LLMProvider",
    "LLMResponse",
    "LocalLLMProvider",
    "OllamaProvider",
    "OpenAIProvider",
    "get_llm_provider",
]


def get_llm_provider() -> LLMProvider:
    from ..config import Settings

    settings = Settings()
    config = LLMConfig(
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        timeout=settings.llm_timeout,
    )

    match settings.llm_provider:
        case "local":
            return LocalLLMProvider(config)
        case "openai":
            return OpenAIProvider(config)
        case "anthropic":
            return AnthropicProvider(config)
        case "ollama":
            return OllamaProvider(config)
        case "fake":
            return FakeLLMProvider(config)
        case _:
            return LocalLLMProvider(config)
