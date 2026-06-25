from __future__ import annotations

import json

import pytest

from app.analysis.pipeline import AnalysisPipeline, PipelineState
from app.analysis.schemas import (
    ExtractionType,
    build_extraction_prompt,
    parse_extraction_response,
)
from app.llm.fake import FakeLLMProvider

EXTRACTION_RESPONSE = json.dumps(
    {
        "entities": [
            {
                "name": "John",
                "type": "character",
                "aliases": ["Johnny"],
                "attributes": {"age": 30},
            },
            {
                "name": "New York",
                "type": "location",
                "aliases": ["NYC"],
                "attributes": {},
            },
        ],
        "facts": [
            {
                "subject": "John",
                "predicate": "lives in",
                "object": "New York",
                "type": "relationship",
            }
        ],
        "summary": "John lives in New York.",
    }
)


def test_build_extraction_prompt() -> None:
    prompt = build_extraction_prompt(1, "Chapter content here")
    assert "Chapter 1" in prompt
    assert "Chapter content here" in prompt


def test_parse_extraction_response_valid() -> None:
    result = parse_extraction_response(EXTRACTION_RESPONSE)
    assert result is not None
    assert len(result.entities) == 2
    assert result.entities[0].name == "John"
    assert result.entities[0].entity_type == ExtractionType.CHARACTER
    assert len(result.facts) == 1
    assert result.summary == "John lives in New York."


def test_parse_extraction_response_invalid() -> None:
    result = parse_extraction_response("No JSON here")
    assert result is None


def test_parse_extraction_response_mixed() -> None:
    text = f"Some text before {EXTRACTION_RESPONSE} and after"
    result = parse_extraction_response(text)
    assert result is not None


@pytest.mark.asyncio
async def test_pipeline_processes_chapters() -> None:
    llm = FakeLLMProvider(responses=[EXTRACTION_RESPONSE])
    pipeline = AnalysisPipeline(llm, max_concurrent=1)

    chapters = [
        {"chapter_number": 1, "content": "Chapter 1 content"},
        {"chapter_number": 2, "content": "Chapter 2 content"},
    ]

    result = await pipeline.analyze_chapters(1, chapters)
    assert result.state == PipelineState.COMPLETED
    assert result.chapters_processed == 2
    assert len(result.entities) > 0


@pytest.mark.asyncio
async def test_pipeline_handles_errors() -> None:
    llm = FakeLLMProvider(responses=["Invalid JSON"])
    pipeline = AnalysisPipeline(llm, max_concurrent=1)

    chapters = [{"chapter_number": 1, "content": "Content"}]
    result = await pipeline.analyze_chapters(1, chapters)
    assert result.state == PipelineState.FAILED
    assert len(result.errors) > 0


@pytest.mark.asyncio
async def test_pipeline_pause_resume() -> None:
    llm = FakeLLMProvider(responses=[EXTRACTION_RESPONSE])
    pipeline = AnalysisPipeline(llm, max_concurrent=1)

    pipeline.pause()
    assert pipeline.state == PipelineState.PAUSED

    pipeline.resume()
    assert pipeline.state != PipelineState.PAUSED


@pytest.mark.asyncio
async def test_pipeline_cancel() -> None:
    llm = FakeLLMProvider(responses=[EXTRACTION_RESPONSE])
    pipeline = AnalysisPipeline(llm, max_concurrent=1)

    pipeline.cancel()
    assert pipeline.state == PipelineState.CANCELLED


def test_pipeline_get_status() -> None:
    llm = FakeLLMProvider()
    pipeline = AnalysisPipeline(llm)
    status = pipeline.get_status()
    assert "state" in status
    assert "tasks" in status
