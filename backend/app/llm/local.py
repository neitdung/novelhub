from __future__ import annotations

from typing import Any

import httpx

from .base import LLMConfig, LLMProvider, LLMResponse


class LocalLLMProvider(LLMProvider):
    def __init__(self, config: LLMConfig | None = None) -> None:
        super().__init__(
            config
            or LLMConfig(
                model="",
                base_url="http://127.0.0.1:10124",
                api_key="not-needed",
            )
        )

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        payload: dict[str, Any] = {
            "messages": messages,
        }
        if self.config.model:
            payload["model"] = self.config.model
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        headers = {
            "Content-Type": "application/json",
        }

        base_url = self.config.base_url.rstrip("/")
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            response = await client.post(
                f"{base_url}/v1/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        choice = data.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "")
        usage_data = data.get("usage", {})
        usage = {
            "prompt_tokens": usage_data.get("prompt_tokens", 0),
            "completion_tokens": usage_data.get("completion_tokens", 0),
            "total_tokens": usage_data.get("total_tokens", 0),
        }
        self.record_usage(usage)

        return LLMResponse(
            content=content,
            model=self.config.model or "local",
            usage=usage,
            finish_reason=choice.get("finish_reason", "stop"),
        )

    async def health_check(self) -> bool:
        try:
            base_url = self.config.base_url.rstrip("/")
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{base_url}/v1/models")
                return response.status_code == 200
        except Exception:
            return False
