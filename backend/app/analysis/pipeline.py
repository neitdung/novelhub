from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from ..llm.base import LLMProvider
from .schemas import (
    ChapterExtraction,
    ExtractedEntity,
    ExtractedFact,
    build_extraction_prompt,
    parse_extraction_response,
)


class PipelineState(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ChapterTask:
    chapter_number: int
    state: PipelineState = PipelineState.PENDING
    attempts: int = 0
    error: str | None = None
    extraction: ChapterExtraction | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class PipelineResult:
    novel_id: int
    state: PipelineState
    chapters_processed: int = 0
    chapters_total: int = 0
    entities: list[ExtractedEntity] = field(default_factory=list)
    facts: list[ExtractedFact] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)


class AnalysisPipeline:
    def __init__(
        self,
        llm: LLMProvider,
        max_concurrent: int = 1,
        max_retries: int = 3,
    ) -> None:
        self.llm = llm
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.tasks: dict[int, ChapterTask] = {}
        self.state = PipelineState.PENDING
        self._cancel_event = asyncio.Event()
        self._pause_event = asyncio.Event()
        self._pause_event.set()

    async def analyze_chapters(
        self,
        novel_id: int,
        chapters: list[dict[str, Any]],
    ) -> PipelineResult:
        self.state = PipelineState.RUNNING
        self._cancel_event.clear()
        self._pause_event.set()

        for ch in chapters:
            num = ch.get("chapter_number", 0)
            self.tasks[num] = ChapterTask(chapter_number=num)

        semaphore = asyncio.Semaphore(self.max_concurrent)
        tasks_list = [
            self._process_chapter(novel_id, ch, semaphore) for ch in chapters
        ]
        await asyncio.gather(*tasks_list, return_exceptions=True)

        all_entities = []
        all_facts = []
        errors = []
        for task in self.tasks.values():
            if task.extraction:
                all_entities.extend(task.extraction.entities)
                all_facts.extend(task.extraction.facts)
            if task.error:
                errors.append(
                    {
                        "chapter": task.chapter_number,
                        "error": task.error,
                    }
                )

        self.state = (
            PipelineState.COMPLETED
            if not errors
            else PipelineState.FAILED
        )

        return PipelineResult(
            novel_id=novel_id,
            state=self.state,
            chapters_processed=len(
                [t for t in self.tasks.values() if t.extraction]
            ),
            chapters_total=len(chapters),
            entities=all_entities,
            facts=all_facts,
            errors=errors,
        )

    async def _process_chapter(
        self,
        novel_id: int,
        chapter: dict[str, Any],
        semaphore: asyncio.Semaphore,
    ) -> None:
        task = self.tasks[chapter.get("chapter_number", 0)]

        async with semaphore:
            while self._pause_event.is_set() is False:
                if self._cancel_event.is_set():
                    task.state = PipelineState.CANCELLED
                    return
                await asyncio.sleep(0.1)

            if self._cancel_event.is_set():
                task.state = PipelineState.CANCELLED
                return

            task.state = PipelineState.RUNNING
            task.started_at = datetime.now()
            task.attempts += 1

            try:
                prompt = build_extraction_prompt(
                    chapter.get("chapter_number", 0),
                    chapter.get("content", ""),
                )
                response = await self.llm.complete(
                    [{"role": "user", "content": prompt}]
                )
                extraction = parse_extraction_response(response.content)
                if extraction:
                    extraction.chapter_number = chapter.get("chapter_number", 0)
                    task.extraction = extraction
                    task.state = PipelineState.COMPLETED
                else:
                    task.error = "Failed to parse extraction response"
                    task.state = PipelineState.FAILED
            except Exception as e:
                task.error = str(e)
                task.state = PipelineState.FAILED
                if task.attempts < self.max_retries:
                    task.state = PipelineState.PENDING

            task.completed_at = datetime.now()

    def pause(self) -> None:
        self._pause_event.clear()
        self.state = PipelineState.PAUSED

    def resume(self) -> None:
        self._pause_event.set()
        self.state = PipelineState.RUNNING

    def cancel(self) -> None:
        self._cancel_event.set()
        self.state = PipelineState.CANCELLED

    def get_status(self) -> dict[str, Any]:
        return {
            "state": self.state.value,
            "tasks": {
                num: {
                    "state": task.state.value,
                    "attempts": task.attempts,
                    "error": task.error,
                }
                for num, task in self.tasks.items()
            },
        }
