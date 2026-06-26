from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile

from ..crud import (
    check_duplicate,
    compute_file_hash,
    create_chapter,
    create_ingest_job,
    create_novel,
    delete_chapter,
    delete_chapters_batch,
    delete_chapters_range,
    get_chapter,
    get_chapter_by_number,
    get_ingest_job,
    get_novel,
    get_source,
    list_chapters,
    list_ingest_jobs,
    swap_chapters,
    update_chapter,
    update_ingest_job,
    update_novel_source,
)
from ..database import get_db_context
from ..parser import split_chapters
from ..schemas import (
    BatchChapterUpdate,
    BatchDeleteRequest,
    ChapterListResponse,
    ChapterResponse,
    ChapterSwapRequest,
    ChapterUpdate,
    ImportJobResponse,
    ImportRequest,
    ImportStatusResponse,
    TxtImportResponse,
)
from ..scraper import get_scraper

router = APIRouter(prefix="/api/novels", tags=["chapters"])
logger = logging.getLogger("chapters")

UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".txt", ".md"}
MAX_FILE_SIZE = 50 * 1024 * 1024

_import_tasks: dict[int, asyncio.Task[None]] = {}


@router.get("/{novel_id}/chapters", response_model=ChapterListResponse)
async def list_novel_chapters(novel_id: int) -> ChapterListResponse:
    async with get_db_context() as db:
        novel = await get_novel(db, novel_id)
        if novel is None:
            raise HTTPException(status_code=404, detail="Novel not found")
        chapters = await list_chapters(db, novel_id)
    return ChapterListResponse(chapters=chapters, total=len(chapters))


@router.get("/{novel_id}/chapters/{chapter_id}", response_model=ChapterResponse)
async def get_novel_chapter(novel_id: int, chapter_id: int) -> ChapterResponse:
    async with get_db_context() as db:
        chapter = await get_chapter(db, chapter_id)
    if chapter is None or chapter["novel_id"] != novel_id:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return ChapterResponse(**chapter)


@router.put("/{novel_id}/chapters/{chapter_id}", response_model=ChapterResponse)
async def update_novel_chapter(
    novel_id: int, chapter_id: int, update: ChapterUpdate
) -> ChapterResponse:
    async with get_db_context() as db:
        chapter = await get_chapter(db, chapter_id)
        if chapter is None or chapter["novel_id"] != novel_id:
            raise HTTPException(status_code=404, detail="Chapter not found")

        success = await update_chapter(
            db,
            chapter_id,
            title=update.title,
            content=update.content,
            raw_content=update.raw_content,
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update chapter")
        updated = await get_chapter(db, chapter_id)
    if updated is None:
        raise HTTPException(status_code=500, detail="Failed to load updated chapter")
    return ChapterResponse(**updated)


@router.post("/{novel_id}/chapters/{chapter_id}/reimport")
async def reimport_chapter(
    novel_id: int,
    chapter_id: int,
    reset_content: bool = False,
) -> ChapterResponse:
    async with get_db_context() as db:
        chapter = await get_chapter(db, chapter_id)
        if chapter is None or chapter["novel_id"] != novel_id:
            raise HTTPException(status_code=404, detail="Chapter not found")

        novel = await get_novel(db, novel_id)
        if novel is None:
            raise HTTPException(status_code=404, detail="Novel not found")

        raw_source_id = novel.get("source_id")
        if raw_source_id is None:
            raise HTTPException(
                status_code=400,
                detail="Novel has no source configured for reimport",
            )
        source_id = int(str(raw_source_id))
        source = await get_source(db, source_id)
        if source is None:
            raise HTTPException(status_code=404, detail="Source not found")

    scraper = get_scraper(source)
    chapter_number = int(str(chapter["chapter_number"]))
    url = str(source["url_template"]).format(
        chapter_id=str(chapter_number),
        chapter_number=str(chapter_number),
    )

    try:
        raw_text = scraper.scrape_one(chapter_number, url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Reimport failed: {e}")

    async with get_db_context() as db:
        await update_chapter(
            db,
            chapter_id,
            raw_content=raw_text,
            content=raw_text if reset_content else None,
        )
        updated = await get_chapter(db, chapter_id)
    if updated is None:
        raise HTTPException(status_code=500, detail="Failed to load chapter")
    return ChapterResponse(**updated)


@router.post("/{novel_id}/chapters/{chapter_id}/reparse")
async def reparse_chapter(novel_id: int, chapter_id: int) -> ChapterResponse:
    async with get_db_context() as db:
        chapter = await get_chapter(db, chapter_id)
        if chapter is None or chapter["novel_id"] != novel_id:
            raise HTTPException(status_code=404, detail="Chapter not found")

        raw = chapter.get("raw_content")
        if not raw:
            raise HTTPException(
                status_code=400, detail="Chapter has no raw_content to reparse"
            )

        parsed = split_chapters(str(raw))
        if parsed:
            new_content = str(parsed[0].get("content", ""))
        else:
            new_content = str(raw)

        await update_chapter(db, chapter_id, content=new_content)
        updated = await get_chapter(db, chapter_id)
    if updated is None:
        raise HTTPException(status_code=500, detail="Failed to load updated chapter")
    return ChapterResponse(**updated)


@router.delete("/{novel_id}/chapters/{chapter_id}")
async def delete_novel_chapter(novel_id: int, chapter_id: int) -> dict[str, str]:
    async with get_db_context() as db:
        chapter = await get_chapter(db, chapter_id)
        if chapter is None or chapter["novel_id"] != novel_id:
            raise HTTPException(status_code=404, detail="Chapter not found")
        await delete_chapter(db, chapter_id)
    return {"status": "deleted"}


@router.post("/{novel_id}/chapters/batch-delete")
async def batch_delete_chapters(
    novel_id: int, request: BatchDeleteRequest
) -> dict[str, int]:
    async with get_db_context() as db:
        if request.chapter_ids:
            deleted = await delete_chapters_batch(db, request.chapter_ids)
        elif request.chapter_start is not None and request.chapter_end is not None:
            deleted = await delete_chapters_range(
                db, novel_id, request.chapter_start, request.chapter_end
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Provide either chapter_ids or chapter_start/chapter_end",
            )
    return {"deleted": deleted}


@router.post("/{novel_id}/chapters/batch-correct")
async def batch_correct_chapters(
    novel_id: int, request: BatchChapterUpdate
) -> ChapterListResponse:
    async with get_db_context() as db:
        for chapter_id, update in zip(request.chapter_ids, request.updates):
            chapter = await get_chapter(db, chapter_id)
            if chapter is None or chapter["novel_id"] != novel_id:
                continue
            await update_chapter(
                db,
                chapter_id,
                title=update.title,
                content=update.content,
                raw_content=update.raw_content,
            )
        chapters = await list_chapters(db, novel_id)
    return ChapterListResponse(chapters=chapters, total=len(chapters))


@router.post("/{novel_id}/chapters/swap")
async def swap_chapter_order(
    novel_id: int, request: ChapterSwapRequest
) -> ChapterListResponse:
    async with get_db_context() as db:
        success = await swap_chapters(db, request.chapter_id_a, request.chapter_id_b)
        if not success:
            raise HTTPException(status_code=400, detail="Invalid chapter IDs")
        chapters = await list_chapters(db, novel_id)
    return ChapterListResponse(chapters=chapters, total=len(chapters))


# --- Import Pipeline ---

async def _run_import(
    job_id: int,
    novel_id: int,
    source_id: int,
    chapter_start: int,
    chapter_end: int,
    url_params: dict[str, str],
) -> None:
    try:
        async with get_db_context() as db:
            source = await get_source(db, source_id)
            if source is None:
                await update_ingest_job(
                    db, job_id, status="failed", error="Source not found"
                )
                return

        scraper = get_scraper(source)
        total = chapter_end - chapter_start + 1

        async with get_db_context() as db:
            await update_ingest_job(db, job_id, status="running", progress=0)

        for i, chapter_num in enumerate(range(chapter_start, chapter_end + 1)):
            try:
                url = str(source["url_template"]).format(
                    chapter_id=str(chapter_num),
                    chapter_number=str(chapter_num),
                    **url_params,
                )
                raw_text = scraper.scrape_one(chapter_num, url)
                raw_lang = source.get("language", "zh")
                lang = str(raw_lang) if raw_lang is not None else "zh"
                parsed = split_chapters(raw_text, language=lang)
                chapter_title = f"Chapter {chapter_num}"
                chapter_content = raw_text
                if parsed:
                    chapter_title = str(parsed[0].get("title", chapter_title))
                    chapter_content = str(parsed[0].get("content", raw_text))

                async with get_db_context() as db:
                    existing = await get_chapter_by_number(db, novel_id, chapter_num)
                    if existing:
                        existing_id = int(str(existing["id"]))
                        await update_chapter(
                            db,
                            existing_id,
                            raw_content=raw_text,
                            content=chapter_content,
                        )
                    else:
                        await create_chapter(
                            db,
                            novel_id,
                            chapter_num,
                            chapter_title,
                            chapter_content,
                            raw_content=raw_text,
                            source_url=url,
                            ingest_job_id=job_id,
                        )

                async with get_db_context() as db:
                    progress = int((i + 1) / total * 100)
                    await update_ingest_job(db, job_id, progress=progress)

            except Exception as e:
                logger.error(f"Import failed for chapter {chapter_num}: {e}")
                async with get_db_context() as db:
                    await update_ingest_job(
                        db, job_id, error=f"Chapter {chapter_num} failed: {e}"
                    )

        async with get_db_context() as db:
            await update_ingest_job(db, job_id, status="completed", progress=100)

    except Exception as e:
        logger.error(f"Import job {job_id} failed: {e}")
        async with get_db_context() as db:
            await update_ingest_job(db, job_id, status="failed", error=str(e))

    finally:
        _import_tasks.pop(job_id, None)


@router.post("/{novel_id}/import", response_model=ImportJobResponse)
async def import_chapters_from_source(
    novel_id: int,
    request: ImportRequest,
    background_tasks: BackgroundTasks,
) -> ImportJobResponse:
    chapter_end = request.chapter_end or request.chapter_start

    async with get_db_context() as db:
        novel = await get_novel(db, novel_id)
        if novel is None:
            raise HTTPException(status_code=404, detail="Novel not found")

        source = await get_source(db, request.source_id)
        if source is None:
            raise HTTPException(status_code=404, detail="Source not found")
        if not source.get("active"):
            raise HTTPException(status_code=400, detail="Source is not active")

        job_id = await create_ingest_job(
            db, novel_id, request.source_id, request.chapter_start, chapter_end
        )
        await update_novel_source(db, novel_id, request.source_id)

    task = asyncio.create_task(
        _run_import(
            job_id,
            novel_id,
            request.source_id,
            request.chapter_start,
            chapter_end,
            request.url_template_params,
        )
    )
    _import_tasks[job_id] = task

    return ImportJobResponse(
        id=job_id,
        novel_id=novel_id,
        source_id=request.source_id,
        chapter_start=request.chapter_start,
        chapter_end=chapter_end,
        status="pending",
        progress=0,
    )


@router.get("/{novel_id}/import/status/{job_id}", response_model=ImportStatusResponse)
async def get_import_status(novel_id: int, job_id: int) -> ImportStatusResponse:
    async with get_db_context() as db:
        job = await get_ingest_job(db, job_id)
    if job is None or int(str(job["novel_id"])) != novel_id:
        raise HTTPException(status_code=404, detail="Import job not found")
    return ImportStatusResponse(
        id=int(str(job["id"])),
        status=str(job["status"]),
        progress=int(str(job.get("progress", 0))),
        error=str(job["error"]) if job.get("error") else None,
    )


@router.get("/{novel_id}/import/jobs", response_model=list[ImportJobResponse])
async def list_import_jobs(novel_id: int) -> list[ImportJobResponse]:
    async with get_db_context() as db:
        jobs = await list_ingest_jobs(db, novel_id)
    return [ImportJobResponse(**j) for j in jobs]


@router.post("/import/txt", response_model=TxtImportResponse)
async def import_txt_file(
    file: UploadFile = File(...),
    title: str = Form(""),
    author: str = Form(""),
    language: str = Form(""),
) -> TxtImportResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not allowed. Use .txt or .md",
        )

    content_bytes = await file.read()
    if len(content_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")

    file_hash = compute_file_hash(content_bytes)

    async with get_db_context() as db:
        if await check_duplicate(db, file_hash):
            raise HTTPException(status_code=409, detail="Duplicate file detected")

        UPLOAD_DIR.mkdir(exist_ok=True)
        file_path = UPLOAD_DIR / f"{file_hash}{ext}"
        file_path.write_bytes(content_bytes)

        novel_title = title or Path(file.filename).stem
        file_lang = language or ""
        novel_id = await create_novel(
            db, novel_title, author, file_lang, file_path, file_hash
        )

        text_content = content_bytes.decode("utf-8-sig")
        parsed = split_chapters(text_content, language=file_lang or None)

        chapters_created = 0
        for ch in parsed:
            await create_chapter(
                db,
                novel_id,
                int(ch["chapter_number"]),
                str(ch["title"]),
                str(ch["content"]),
                raw_content=str(ch["content"]),
            )
            chapters_created += 1

    return TxtImportResponse(
        novel_id=novel_id,
        chapters_created=chapters_created,
        title=novel_title,
    )
