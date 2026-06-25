from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_health_includes_database_status(client: AsyncClient) -> None:
    response = await client.get("/api/health")
    data = response.json()
    assert "database" in data
    assert data["database"] == "ok"


@pytest.mark.asyncio
async def test_health_response_model(client: AsyncClient) -> None:
    response = await client.get("/api/health")
    data = response.json()
    assert isinstance(data, dict)
    assert "status" in data
