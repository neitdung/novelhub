from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..crud import (
    create_bookmark,
    delete_bookmark,
    get_bookmarks,
    get_progress,
    update_progress,
)
from ..database import get_db_context
from ..schemas import BookmarkCreate, BookmarkList, BookmarkResponse, ProgressResponse

router = APIRouter(prefix="/api", tags=["bookmarks"])


@router.post("/novels/{novel_id}/bookmarks", response_model=BookmarkResponse)
async def create_novel_bookmark(
    novel_id: int, bookmark: BookmarkCreate
) -> BookmarkResponse:
    async with get_db_context() as db:
        bookmark_id = await create_bookmark(
            db, novel_id, bookmark.chapter_id, bookmark.position, bookmark.title
        )
    return BookmarkResponse(
        id=bookmark_id,
        novel_id=novel_id,
        chapter_id=bookmark.chapter_id,
        position=bookmark.position,
        title=bookmark.title,
    )


@router.get("/novels/{novel_id}/bookmarks", response_model=BookmarkList)
async def list_novel_bookmarks(novel_id: int) -> BookmarkList:
    async with get_db_context() as db:
        bookmarks = await get_bookmarks(db, novel_id)
    return BookmarkList(bookmarks=bookmarks, total=len(bookmarks))


@router.delete("/novels/{novel_id}/bookmarks/{bookmark_id}")
async def delete_novel_bookmark(novel_id: int, bookmark_id: int) -> dict[str, str]:
    async with get_db_context() as db:
        deleted = await delete_bookmark(db, novel_id, bookmark_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return {"status": "deleted"}


@router.get("/novels/{novel_id}/progress", response_model=ProgressResponse)
async def get_novel_progress(novel_id: int) -> ProgressResponse:
    async with get_db_context() as db:
        progress = await get_progress(db, novel_id)
    if progress is None:
        return ProgressResponse(novel_id=novel_id, chapter_id=0, position=0)
    return ProgressResponse(**progress)


@router.put("/novels/{novel_id}/progress", response_model=ProgressResponse)
async def update_novel_progress(
    novel_id: int, progress: ProgressResponse
) -> ProgressResponse:
    async with get_db_context() as db:
        await update_progress(db, novel_id, progress.chapter_id, progress.position)
    return progress
