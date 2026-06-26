from __future__ import annotations

import io
from pathlib import Path

import pytest
from httpx import AsyncClient

from app.crud import (
    create_chapter,
    create_ingest_job,
    create_source,
    delete_chapter,
    delete_chapters_range,
    delete_source,
    get_chapter,
    get_chapter_by_number,
    get_ingest_job,
    get_source,
    list_chapters,
    list_sources,
    swap_chapters,
    update_chapter,
    update_ingest_job,
    update_source,
)
from app.crud import create_novel as crud_create_novel
from app.database import get_db_context
from app.scraper import BaseScraper, ScrapeError, ShubaScraper, get_scraper

# --- Source CRUD Tests ---

@pytest.mark.asyncio
async def test_create_source(client: AsyncClient) -> None:
    response = await client.post(
        "/api/sources/",
        json={
            "name": "69shuba",
            "url_template": "https://www.69shuba.com/txt/{novel_id}/{chapter_id}",
            "css_selector": ".txtnav",
            "language": "zh",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "69shuba"
    assert "id" in data
    assert data["active"] is True


@pytest.mark.asyncio
async def test_list_sources(client: AsyncClient) -> None:
    response = await client.get("/api/sources/")
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_update_source(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/api/sources/",
        json={
            "name": "Test",
            "url_template": "http://example.com/{chapter_id}",
            "language": "en",
        },
    )
    source_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/sources/{source_id}",
        json={"name": "Updated Source", "active": False},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Source"
    assert response.json()["active"] is False


@pytest.mark.asyncio
async def test_delete_source(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/api/sources/",
        json={
            "name": "Delete Me",
            "url_template": "http://example.com/{chapter_id}",
            "language": "en",
        },
    )
    source_id = create_resp.json()["id"]

    response = await client.delete(f"/api/sources/{source_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


@pytest.mark.asyncio
async def test_delete_source_not_found(client: AsyncClient) -> None:
    response = await client.delete("/api/sources/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_seed_default_sources(client: AsyncClient) -> None:
    response = await client.post("/api/sources/defaults")
    assert response.status_code == 200
    data = response.json()
    names = {s["name"] for s in data["sources"]}
    assert "69shuba" in names


# --- Chapter Handler Tests ---

@pytest.mark.asyncio
async def test_list_chapters(client: AsyncClient) -> None:
    novel_resp = await client.post(
        "/api/novels/",
        files={"file": ("test.txt", io.BytesIO(b"Chapter 1\n\nContent"), "text/plain")},
        data={"title": "Chapters Test", "language": "en"},
    )
    novel_id = novel_resp.json()["id"]

    async with get_db_context() as db:
        await create_chapter(db, novel_id, 1, "Chapter 1", "Content 1")
        await create_chapter(db, novel_id, 2, "Chapter 2", "Content 2")

    response = await client.get(f"/api/novels/{novel_id}/chapters")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["chapters"]) == 2


@pytest.mark.asyncio
async def test_get_chapter(client: AsyncClient) -> None:
    novel_resp = await client.post(
        "/api/novels/",
        files={"file": ("test.txt", io.BytesIO(b"Content"), "text/plain")},
        data={"title": "Get Chapter Test"},
    )
    novel_id = novel_resp.json()["id"]

    async with get_db_context() as db:
        ch_id = await create_chapter(db, novel_id, 1, "Ch1", "Hello World")

    response = await client.get(f"/api/novels/{novel_id}/chapters/{ch_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Ch1"
    assert "raw_content" in response.json()


@pytest.mark.asyncio
async def test_update_chapter_content(client: AsyncClient) -> None:
    novel_resp = await client.post(
        "/api/novels/",
        files={"file": ("test.txt", io.BytesIO(b"Content"), "text/plain")},
        data={"title": "Update Test"},
    )
    novel_id = novel_resp.json()["id"]

    async with get_db_context() as db:
        ch_id = await create_chapter(db, novel_id, 1, "Ch1", "Old Content")

    response = await client.put(
        f"/api/novels/{novel_id}/chapters/{ch_id}",
        json={
            "title": "Updated Ch1",
            "content": "New Content",
            "raw_content": "New Raw",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Ch1"
    assert data["content"] == "New Content"
    assert data["is_corrected"] is True


@pytest.mark.asyncio
async def test_delete_chapter(client: AsyncClient) -> None:
    novel_resp = await client.post(
        "/api/novels/",
        files={"file": ("test.txt", io.BytesIO(b"Content"), "text/plain")},
        data={"title": "Delete Test"},
    )
    novel_id = novel_resp.json()["id"]

    async with get_db_context() as db:
        ch_id = await create_chapter(db, novel_id, 1, "Ch1", "Content")

    response = await client.delete(f"/api/novels/{novel_id}/chapters/{ch_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


@pytest.mark.asyncio
async def test_batch_delete_chapters(client: AsyncClient) -> None:
    novel_resp = await client.post(
        "/api/novels/",
        files={"file": ("test.txt", io.BytesIO(b"Content"), "text/plain")},
        data={"title": "Batch Delete"},
    )
    novel_id = novel_resp.json()["id"]

    async with get_db_context() as db:
        await create_chapter(db, novel_id, 1, "Ch1", "Content 1")
        await create_chapter(db, novel_id, 2, "Ch2", "Content 2")
        await create_chapter(db, novel_id, 3, "Ch3", "Content 3")

    response = await client.post(
        f"/api/novels/{novel_id}/chapters/batch-delete",
        json={"chapter_ids": [1, 2]},
    )
    assert response.status_code == 200

    chapters_resp = await client.get(f"/api/novels/{novel_id}/chapters")
    assert chapters_resp.json()["total"] == 1


@pytest.mark.asyncio
async def test_batch_delete_range(client: AsyncClient) -> None:
    novel_resp = await client.post(
        "/api/novels/",
        files={"file": ("test.txt", io.BytesIO(b"Content"), "text/plain")},
        data={"title": "Batch Range"},
    )
    novel_id = novel_resp.json()["id"]

    async with get_db_context() as db:
        await create_chapter(db, novel_id, 1, "Ch1", "C1")
        await create_chapter(db, novel_id, 2, "Ch2", "C2")
        await create_chapter(db, novel_id, 3, "Ch3", "C3")

    response = await client.post(
        f"/api/novels/{novel_id}/chapters/batch-delete",
        json={"chapter_start": 2, "chapter_end": 3},
    )
    assert response.status_code == 200
    assert response.json()["deleted"] == 2


@pytest.mark.asyncio
async def test_swap_chapters(client: AsyncClient) -> None:
    novel_resp = await client.post(
        "/api/novels/",
        files={"file": ("test.txt", io.BytesIO(b"Content"), "text/plain")},
        data={"title": "Swap Test"},
    )
    novel_id = novel_resp.json()["id"]

    async with get_db_context() as db:
        id_a = await create_chapter(db, novel_id, 1, "Ch1", "First")
        id_b = await create_chapter(db, novel_id, 2, "Ch2", "Second")

        response = await client.post(
            f"/api/novels/{novel_id}/chapters/swap",
            json={"chapter_id_a": id_a, "chapter_id_b": id_b},
        )
    assert response.status_code == 200

    ch_a = await client.get(f"/api/novels/{novel_id}/chapters/{id_a}")
    ch_b = await client.get(f"/api/novels/{novel_id}/chapters/{id_b}")
    ch_a_num = ch_a.json()["chapter_number"]
    ch_b_num = ch_b.json()["chapter_number"]
    assert (ch_a_num, ch_b_num) == (2, 1)


@pytest.mark.asyncio
async def test_get_chapter_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/novels/1/chapters/999")
    assert response.status_code == 404


# --- Reparse Tests ---

@pytest.mark.asyncio
async def test_reparse_chapter(client: AsyncClient) -> None:
    novel_resp = await client.post(
        "/api/novels/",
        files={"file": ("test.txt", io.BytesIO(b"Content"), "text/plain")},
        data={"title": "Reparse Test"},
    )
    novel_id = novel_resp.json()["id"]

    async with get_db_context() as db:
        ch_id = await create_chapter(
            db, novel_id, 1, "Ch1", "Old Content",
            raw_content="Chapter 1: New\n\nThis is reparsed content."
        )

    response = await client.post(f"/api/novels/{novel_id}/chapters/{ch_id}/reparse")
    assert response.status_code == 200
    assert "New" in response.json().get("raw_content", "")
    assert response.json()["is_corrected"] is True


@pytest.mark.asyncio
async def test_reparse_no_raw_content(client: AsyncClient) -> None:
    novel_resp = await client.post(
        "/api/novels/",
        files={"file": ("test.txt", io.BytesIO(b"Content"), "text/plain")},
        data={"title": "No Raw"},
    )
    novel_id = novel_resp.json()["id"]

    async with get_db_context() as db:
        ch_id = await create_chapter(db, novel_id, 1, "Ch1", "Content")

    response = await client.post(f"/api/novels/{novel_id}/chapters/{ch_id}/reparse")
    assert response.status_code == 400


# --- Scraper Unit Tests ---

def test_base_scraper_raises_on_bad_url() -> None:
    scraper = BaseScraper(max_retries=1, delay=0.1)
    with pytest.raises(ScrapeError):
        scraper.scrape_one(1, "")


def test_shuba_scraper_skip_prefixes() -> None:
    scraper = ShubaScraper()
    assert scraper.SKIP_PREFIXES is not None
    assert "loadAdv" in scraper.SKIP_PREFIXES


def test_get_scraper_factory() -> None:
    shuba_source = {"name": "69shuba", "css_selector": ".txtnav"}
    scraper = get_scraper(shuba_source)
    assert isinstance(scraper, ShubaScraper)

    generic_source = {"name": "generic", "css_selector": ".content"}
    scraper2 = get_scraper(generic_source)
    assert isinstance(scraper2, ShubaScraper)


@pytest.mark.asyncio
async def test_scraper_fetch_fails_without_scrapling() -> None:
    scraper = ShubaScraper(max_retries=1, delay=0.1)
    with pytest.raises(ScrapeError, match="scrapling not installed"):
        scraper.fetch_chapter(1, "http://example.com")


# --- Txt Import Tests ---

@pytest.mark.asyncio
async def test_import_txt_file_with_chapters(client: AsyncClient) -> None:
    content = (
        b"Chapter 1: Begin\n\nFirst content.\n\nChapter 2: Middle\n\nSecond content."
    )
    response = await client.post(
        "/api/novels/import/txt",
        files={"file": ("novel.txt", io.BytesIO(content), "text/plain")},
        data={"title": "Imported Novel", "author": "Author", "language": "en"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["chapters_created"] == 2
    assert data["title"] == "Imported Novel"
    assert "novel_id" in data


@pytest.mark.asyncio
async def test_import_txt_duplicate(client: AsyncClient) -> None:
    content = b"Some unique content for duplicate test."
    await client.post(
        "/api/novels/import/txt",
        files={"file": ("novel.txt", io.BytesIO(content), "text/plain")},
        data={"title": "First"},
    )
    response = await client.post(
        "/api/novels/import/txt",
        files={"file": ("novel.txt", io.BytesIO(content), "text/plain")},
        data={"title": "Duplicate"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_import_txt_invalid_extension(client: AsyncClient) -> None:
    response = await client.post(
        "/api/novels/import/txt",
        files={"file": ("novel.pdf", io.BytesIO(b"test"), "application/pdf")},
    )
    assert response.status_code == 400


# --- Import Job Tests ---

@pytest.mark.asyncio
async def test_import_job_lifecycle(client: AsyncClient) -> None:
    novel_resp = await client.post(
        "/api/novels/",
        files={"file": ("test.txt", io.BytesIO(b"Content"), "text/plain")},
        data={"title": "Import Job Test"},
    )
    novel_id = novel_resp.json()["id"]

    source_resp = await client.post(
        "/api/sources/",
        json={
            "name": "test-source",
            "url_template": "http://example.com/{chapter_id}",
            "language": "en",
        },
    )
    source_id = source_resp.json()["id"]

    async with get_db_context() as db:
        job_id = await create_ingest_job(db, novel_id, source_id, 1, 3)

    status_resp = await client.get(f"/api/novels/{novel_id}/import/status/{job_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "pending"

    jobs_resp = await client.get(f"/api/novels/{novel_id}/import/jobs")
    assert jobs_resp.status_code == 200
    assert len(jobs_resp.json()) >= 1


@pytest.mark.asyncio
async def test_import_start_fails_without_active_source(client: AsyncClient) -> None:
    novel_resp = await client.post(
        "/api/novels/",
        files={"file": ("test.txt", io.BytesIO(b"Content"), "text/plain")},
        data={"title": "No Source"},
    )
    novel_id = novel_resp.json()["id"]

    response = await client.post(
        f"/api/novels/{novel_id}/import",
        json={"source_id": 999, "chapter_start": 1, "chapter_end": 1},
    )
    assert response.status_code == 404


# --- CRUD Unit Tests ---

@pytest.mark.asyncio
async def test_crud_source_operations() -> None:
    async with get_db_context() as db:
        sid = await create_source(
            db, "test", "http://example.com/{chapter_id}", ".content", "en", True
        )
        assert sid > 0

        sources = await list_sources(db)
        assert len(sources) >= 1

        source = await get_source(db, sid)
        assert source is not None
        assert source["name"] == "test"

        await update_source(db, sid, {"name": "updated"})
        updated = await get_source(db, sid)
        assert updated is not None
        assert updated["name"] == "updated"

        assert await delete_source(db, sid)
        assert await get_source(db, sid) is None


@pytest.mark.asyncio
async def test_crud_chapter_operations() -> None:
    async with get_db_context() as db:
        nid = await crud_create_novel(
            db, "Test", "Author", "en", Path("test.txt"), "hash123"
        )

        cid = await create_chapter(
            db, nid, 1, "Ch1", "Content", raw_content="Raw"
        )
        assert cid > 0

        chapters = await list_chapters(db, nid)
        assert len(chapters) == 1

        ch = await get_chapter(db, cid)
        assert ch is not None
        assert ch["raw_content"] == "Raw"

        await update_chapter(db, cid, title="Updated", content="New Content")
        updated = await get_chapter(db, cid)
        assert updated is not None
        assert updated["is_corrected"] == 1

        by_num = await get_chapter_by_number(db, nid, 1)
        assert by_num is not None

        assert await delete_chapter(db, cid)
        assert await get_chapter(db, cid) is None


@pytest.mark.asyncio
async def test_crud_ingest_job() -> None:
    async with get_db_context() as db:
        nid = await crud_create_novel(db, "Test", "A", "en", Path("t.txt"), "h1")
        sid = await create_source(
            db, "s", "http://e.com/{chapter_id}", ".c", "en", True
        )
        jid = await create_ingest_job(db, nid, sid, 1, 5)
        assert jid > 0

        job = await get_ingest_job(db, jid)
        assert job is not None
        assert job["status"] == "pending"

        await update_ingest_job(db, jid, status="running", progress=50)
        updated = await get_ingest_job(db, jid)
        assert updated is not None
        assert updated["status"] == "running"
        assert updated["progress"] == 50

        await update_ingest_job(db, jid, status="completed", progress=100)
        done = await get_ingest_job(db, jid)
        assert done is not None
        assert done["status"] == "completed"


@pytest.mark.asyncio
async def test_swap_chapters_swap() -> None:
    async with get_db_context() as db:
        nid = await crud_create_novel(db, "Swap", "A", "en", Path("s.txt"), "h2")
        id_a = await create_chapter(db, nid, 1, "First", "Content A")
        id_b = await create_chapter(db, nid, 2, "Second", "Content B")

        assert await swap_chapters(db, id_a, id_b)

        ch_a = await get_chapter(db, id_a)
        ch_b = await get_chapter(db, id_b)
        assert ch_a is not None
        assert ch_b is not None
        assert ch_a["chapter_number"] == 2
        assert ch_b["chapter_number"] == 1


@pytest.mark.asyncio
async def test_delete_chapters_range() -> None:
    async with get_db_context() as db:
        nid = await crud_create_novel(
            db, "Range Delete", "A", "en", Path("r.txt"), "h3"
        )
        await create_chapter(db, nid, 1, "C1", "X")
        await create_chapter(db, nid, 2, "C2", "X")
        await create_chapter(db, nid, 3, "C3", "X")

        deleted = await delete_chapters_range(db, nid, 2, 3)
        assert deleted == 2

        remaining = await list_chapters(db, nid)
        assert len(remaining) == 1
