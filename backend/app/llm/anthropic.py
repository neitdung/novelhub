from __future__ import annotations

from typing import Any

import httpx

from .base import LLMConfig, LLMProvider, LLMResponse


class AnthropicProvider(LLMProvider):
    def __init__(self, config: LLMConfig | None = None) -> None:
        super().__init__(config or LLMConfig(model="claude-3-haiku-20240307"))
        if not self.config.api_key:
            raise ValueError("Anthropic API key is required")

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        system_msg = ""
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append(msg)

        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": user_messages,
            "max_tokens": max_tokens or 4096,
        }
        if system_msg:
            payload["system"] = system_msg
        if temperature is not None:
            payload["temperature"] = temperature

        headers = {
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        content_blocks = data.get("content", [])
        content = ""
        for block in content_blocks:
            if block.get("type") == "text":
                content += block.get("text", "")

        usage_data = data.get("usage", {})
        usage = {
            "prompt_tokens": usage_data.get("input_tokens", 0),
            "completion_tokens": usage_data.get("output_tokens", 0),
            "total_tokens": usage_data.get("input_tokens", 0)
            + usage_data.get("output_tokens", 0),
        }
        self.record_usage(usage)

        return LLMResponse(
            content=content,
            model=self.config.model,
            usage=usage,
            finish_reason=data.get("stop_reason", "end_turn"),
        )

    async def health_check(self) -> bool:
        try:
            headers = {
                "x-api-key": self.config.api_key,
                "anthropic-version": "2023-06-01",
            }
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    "https://api.anthropic.com/v1/models",
                    headers=headers,
                )
                return response.status_code == 200
        except Exception:
            return False
