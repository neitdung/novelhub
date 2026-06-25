from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)
    finish_reason: str = "stop"


@dataclass
class LLMConfig:
    model: str = "llama3.2"
    base_url: str = "http://localhost:11434"
    api_key: str = ""
    timeout: float = 60.0
    max_retries: int = 3
    temperature: float = 0.7


class LLMProvider(ABC):
    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self.total_tokens = 0
        self.total_cost = 0.0

    @abstractmethod
    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass

    def record_usage(self, usage: dict[str, int], cost: float = 0.0) -> None:
        self.total_tokens += usage.get("total_tokens", 0)
        self.total_cost += cost

    def get_usage(self) -> dict[str, Any]:
        return {
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
        }
