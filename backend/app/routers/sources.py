from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..crud import (
    count_novels_for_source,
    create_source,
    delete_source,
    get_source,
    list_sources,
    update_source,
)
from ..database import get_db_context
from ..parser import split_chapters
from ..schemas import (
    ImportPreviewChapter,
    ImportPreviewResponse,
    SourceCreate,
    SourceList,
    SourceResponse,
    SourceUpdate,
)

router = APIRouter(prefix="/api/sources", tags=["sources"])

DEFAULT_SOURCES: list[dict[str, object]] = [
    {
        "name": "69shuba",
        "url_template": "https://www.69shuba.com/txt/{novel_id}/{chapter_id}",
        "css_selector": ".txtnav",
        "language": "zh",
        "active": True,
    },
]


@router.get("/", response_model=SourceList)
async def get_sources() -> SourceList:
    async with get_db_context() as db:
        sources = await list_sources(db)
    return SourceList(sources=sources, total=len(sources))


@router.post("/", response_model=SourceResponse, status_code=201)
async def create_new_source(source: SourceCreate) -> SourceResponse:
    async with get_db_context() as db:
        source_id = await create_source(
            db,
            source.name,
            source.url_template,
            source.css_selector,
            source.language,
            source.active,
        )
        created = await get_source(db, source_id)
    if created is None:
        raise HTTPException(status_code=500, detail="Failed to create source")
    return SourceResponse(**created)


@router.put("/{source_id}", response_model=SourceResponse)
async def update_existing_source(
    source_id: int, source: SourceUpdate
) -> SourceResponse:
    updates = source.model_dump(exclude_none=True)
    if "active" in updates:
        updates["active"] = int(updates["active"])
    async with get_db_context() as db:
        existing = await get_source(db, source_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Source not found")
        await update_source(db, source_id, updates)
        updated = await get_source(db, source_id)
    if updated is None:
        raise HTTPException(status_code=500, detail="Failed to update source")
    return SourceResponse(**updated)


@router.delete("/{source_id}")
async def delete_existing_source(source_id: int) -> dict[str, str]:
    async with get_db_context() as db:
        existing = await get_source(db, source_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Source not found")
        novel_count = await count_novels_for_source(db, source_id)
        if novel_count > 0:
            raise HTTPException(
                status_code=409,
                detail=f"Cannot delete source: {novel_count} novel(s) reference it",
            )
        await delete_source(db, source_id)
    return {"status": "deleted"}


@router.post("/{source_id}/preview", response_model=ImportPreviewResponse)
async def preview_source_chapters(
    source_id: int,
    chapter_start: int = 1,
    chapter_end: int | None = None,
) -> ImportPreviewResponse:
    async with get_db_context() as db:
        source = await get_source(db, source_id)
        if source is None:
            raise HTTPException(status_code=404, detail="Source not found")
        if not source.get("active"):
            raise HTTPException(status_code=400, detail="Source is not active")

        novels_cursor = await db.execute(
            "SELECT id, title FROM novels WHERE source_id = ? ORDER BY title",
            (source_id,),
        )
        novels = list(await novels_cursor.fetchall())

    if not novels:
        raise HTTPException(
            status_code=400,
            detail="No novels associated with this source",
        )

    novel_id = int(str(novels[0][0]))

    end = chapter_end or chapter_start + 9
    from ..scraper import get_scraper

    scraper = get_scraper(source)
    chapters: list[ImportPreviewChapter] = []

    for ch_num in range(chapter_start, end + 1):
        try:
            url = str(source["url_template"]).format(
                chapter_id=str(ch_num),
                chapter_number=str(ch_num),
            )
            raw_text = scraper.scrape_one(ch_num, url)
            raw_lang = source.get("language", "zh")
            lang = str(raw_lang) if raw_lang is not None else "zh"
            parsed = split_chapters(raw_text, language=lang)
            title = f"Chapter {ch_num}"
            content_preview = ""
            content_length = len(raw_text)
            if parsed:
                title = str(parsed[0].get("title", title))
                content = str(parsed[0].get("content", raw_text))
                content_preview = (
                    content[:200] + "..." if len(content) > 200 else content
                )
            else:
                content_preview = (
                    raw_text[:200] + "..." if len(raw_text) > 200 else raw_text
                )

            chapters.append(
                ImportPreviewChapter(
                    chapter_number=ch_num,
                    title=title,
                    content_preview=content_preview,
                    content_length=content_length,
                )
            )
        except Exception as e:
            chapters.append(
                ImportPreviewChapter(
                    chapter_number=ch_num,
                    title=f"Chapter {ch_num}",
                    content_preview=f"[Failed to fetch: {e}]",
                    content_length=0,
                )
            )

    return ImportPreviewResponse(
        novel_id=novel_id,
        chapters=chapters,
        total_chapters=len(chapters),
    )


@router.post("/defaults")
async def seed_default_sources() -> SourceList:
    async with get_db_context() as db:
        existing = await list_sources(db)
        existing_names = {s["name"] for s in existing}
        for src in DEFAULT_SOURCES:
            if src["name"] not in existing_names:
                await create_source(
                    db,
                    str(src["name"]),
                    str(src["url_template"]),
                    str(src["css_selector"]),
                    str(src["language"]),
                    bool(src["active"]),
                )
        sources = await list_sources(db)
    return SourceList(sources=sources, total=len(sources))
