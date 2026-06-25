from __future__ import annotations

import io

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_novel(client: AsyncClient) -> None:
    content = b"This is a test novel content."
    response = await client.post(
        "/api/novels/",
        files={"file": ("test.txt", io.BytesIO(content), "text/plain")},
        data={"title": "Test Novel", "author": "Test Author", "language": "en"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Novel"
    assert data["author"] == "Test Author"
    assert "id" in data
    assert "file_hash" in data


@pytest.mark.asyncio
async def test_upload_novel_invalid_extension(client: AsyncClient) -> None:
    content = b"test content"
    response = await client.post(
        "/api/novels/",
        files={"file": ("test.exe", io.BytesIO(content), "application/octet-stream")},
    )
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_novels(client: AsyncClient) -> None:
    response = await client.get("/api/novels/")
    assert response.status_code == 200
    data = response.json()
    assert "novels" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_novel(client: AsyncClient) -> None:
    content = b"Test content"
    upload_response = await client.post(
        "/api/novels/",
        files={"file": ("test.txt", io.BytesIO(content), "text/plain")},
        data={"title": "Test Novel", "author": "Author", "language": "en"},
    )
    novel_id = upload_response.json()["id"]

    response = await client.get(f"/api/novels/{novel_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Novel"


@pytest.mark.asyncio
async def test_get_novel_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/novels/999")
    assert response.status_code == 404
