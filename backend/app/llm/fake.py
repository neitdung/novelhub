from __future__ import annotations

import random

from .base import LLMConfig, LLMProvider, LLMResponse


class FakeLLMProvider(LLMProvider):
    def __init__(
        self,
        config: LLMConfig | None = None,
        responses: list[str] | None = None,
        fail_rate: float = 0.0,
        timeout_rate: float = 0.0,
    ) -> None:
        super().__init__(config or LLMConfig(model="fake"))
        self.responses = responses or ["Fake response"]
        self.response_index = 0
        self.fail_rate = fail_rate
        self.timeout_rate = timeout_rate
        self.call_count = 0

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        self.call_count += 1

        if random.random() < self.timeout_rate:
            raise TimeoutError("Fake timeout")

        if random.random() < self.fail_rate:
            raise RuntimeError("Fake error")

        content = self.responses[self.response_index % len(self.responses)]
        self.response_index += 1

        usage = {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        }
        self.record_usage(usage)

        return LLMResponse(
            content=content,
            model="fake",
            usage=usage,
        )

    async def health_check(self) -> bool:
        return True

    def reset(self) -> None:
        self.response_index = 0
        self.call_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0
