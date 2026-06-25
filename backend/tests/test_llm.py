from __future__ import annotations

import pytest

from app.llm.fake import FakeLLMProvider


@pytest.mark.asyncio
async def test_fake_llm_returns_response() -> None:
    llm = FakeLLMProvider()
    response = await llm.complete([{"role": "user", "content": "Hello"}])
    assert response.content == "Fake response"
    assert response.model == "fake"


@pytest.mark.asyncio
async def test_fake_llm_tracks_usage() -> None:
    llm = FakeLLMProvider()
    await llm.complete([{"role": "user", "content": "Hello"}])
    usage = llm.get_usage()
    assert usage["total_tokens"] > 0


@pytest.mark.asyncio
async def test_fake_llm_health_check() -> None:
    llm = FakeLLMProvider()
    assert await llm.health_check()


@pytest.mark.asyncio
async def test_fake_llm_reset() -> None:
    llm = FakeLLMProvider()
    await llm.complete([{"role": "user", "content": "Hello"}])
    llm.reset()
    assert llm.call_count == 0
    assert llm.total_tokens == 0


@pytest.mark.asyncio
async def test_fake_llm_multiple_responses() -> None:
    llm = FakeLLMProvider(responses=["First", "Second", "Third"])
    r1 = await llm.complete([{"role": "user", "content": "1"}])
    r2 = await llm.complete([{"role": "user", "content": "2"}])
    r3 = await llm.complete([{"role": "user", "content": "3"}])
    assert r1.content == "First"
    assert r2.content == "Second"
    assert r3.content == "Third"
