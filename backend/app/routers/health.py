from __future__ import annotations

from fastapi import APIRouter

from ..config import Settings
from ..llm.anthropic import AnthropicProvider
from ..llm.base import LLMConfig, LLMProvider
from ..llm.local import LocalLLMProvider
from ..llm.ollama import OllamaProvider
from ..llm.openai import OpenAIProvider
from ..schemas import (
    HealthCheckResponse,
    ModelInfo,
    ModelsListResponse,
    ProviderStatus,
)

router = APIRouter(prefix="/api/health", tags=["health"])


def _get_provider_instances() -> list[tuple[str, str, LLMProvider]]:
    """Return list of (provider_name, display_name, provider_instance) tuples."""
    settings = Settings()
    providers: list[tuple[str, str, LLMProvider]] = []

    # Local provider
    local_config = LLMConfig(
        base_url=settings.llm_base_url or "http://127.0.0.1:10124",
        api_key="not-needed",
    )
    providers.append(("local", "Local LLM", LocalLLMProvider(local_config)))

    # Ollama
    ollama_config = LLMConfig(
        base_url=settings.llm_base_url or "http://localhost:11434",
    )
    providers.append(("ollama", "Ollama", OllamaProvider(ollama_config)))

    # OpenAI-compatible
    if settings.llm_api_key:
        openai_config = LLMConfig(
            base_url=settings.llm_base_url or "https://api.openai.com/v1",
            api_key=settings.llm_api_key,
        )
        providers.append(("openai", "OpenAI", OpenAIProvider(openai_config)))

    # Anthropic
    if settings.llm_api_key:
        try:
            anthropic_config = LLMConfig(
                api_key=settings.llm_api_key,
            )
            providers.append(
                ("anthropic", "Anthropic", AnthropicProvider(anthropic_config))
            )
        except ValueError:
            pass

    return providers


@router.get("/providers", response_model=HealthCheckResponse)
async def get_providers_health() -> HealthCheckResponse:
    """Check health status of all configured LLM providers."""
    providers_list: list[ProviderStatus] = []

    for provider_id, display_name, provider in _get_provider_instances():
        try:
            healthy = await provider.health_check()
            providers_list.append(
                ProviderStatus(
                    provider=provider_id,
                    name=display_name,
                    healthy=healthy,
                )
            )
        except Exception as e:
            providers_list.append(
                ProviderStatus(
                    provider=provider_id,
                    name=display_name,
                    healthy=False,
                    error=str(e),
                )
            )

    return HealthCheckResponse(providers=providers_list)


@router.get("/models", response_model=ModelsListResponse)
async def get_available_models() -> ModelsListResponse:
    """List available models from configured providers."""
    models_list: list[ModelInfo] = []
    settings = Settings()

    # Try to get models from Ollama
    try:
        import httpx

        ollama_base = settings.llm_base_url or "http://localhost:11434"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{ollama_base}/api/tags")
            if response.status_code == 200:
                data = response.json()
                for model in data.get("models", []):
                    models_list.append(
                        ModelInfo(
                            provider="ollama",
                            name=str(model.get("name", "unknown")),
                            model_id=str(model.get("name", "unknown")),
                        )
                    )
    except Exception:
        # Ollama not available, add default model
        models_list.append(
            ModelInfo(
                provider="ollama",
                name="llama3.2 (default)",
                model_id="llama3.2",
            )
        )

    # Try to get models from OpenAI-compatible endpoint
    if settings.llm_api_key:
        try:
            import httpx

            openai_base = (settings.llm_base_url or "https://api.openai.com/v1").rstrip(
                "/"
            )
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{openai_base}/v1/models",
                    headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                )
                if response.status_code == 200:
                    data = response.json()
                    for model in data.get("data", []):
                        models_list.append(
                            ModelInfo(
                                provider="openai",
                                name=str(model.get("id", "unknown")),
                                model_id=str(model.get("id", "unknown")),
                            )
                        )
        except Exception:
            models_list.append(
                ModelInfo(
                    provider="openai",
                    name="gpt-4o-mini (default)",
                    model_id="gpt-4o-mini",
                )
            )

    # Add Anthropic default models
    if settings.llm_api_key:
        models_list.append(
            ModelInfo(
                provider="anthropic",
                name="claude-3-haiku",
                model_id="claude-3-haiku-20240307",
            )
        )
        models_list.append(
            ModelInfo(
                provider="anthropic",
                name="claude-3-sonnet",
                model_id="claude-3-sonnet-20240229",
            )
        )

    return ModelsListResponse(models=models_list)
