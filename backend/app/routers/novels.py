from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..crud import (
    check_duplicate,
    compute_file_hash,
    create_novel,
    get_novel,
    list_novels,
)
from ..database import get_db_context
from ..schemas import NovelList, NovelResponse

router = APIRouter(prefix="/api/novels", tags=["novels"])

UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".txt", ".md"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("/", response_model=NovelResponse)
async def upload_novel(
    file: UploadFile = File(...),
    title: str = Form(""),
    author: str = Form(""),
    language: str = Form("en"),
) -> NovelResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not allowed. Use .txt or .md",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")

    file_hash = compute_file_hash(content)

    async with get_db_context() as db:
        if await check_duplicate(db, file_hash):
            raise HTTPException(status_code=409, detail="Duplicate file detected")

        UPLOAD_DIR.mkdir(exist_ok=True)
        file_path = UPLOAD_DIR / f"{file_hash}{ext}"
        file_path.write_bytes(content)

        novel_title = title or Path(file.filename).stem
        novel_id = await create_novel(
            db, novel_title, author, language, file_path, file_hash
        )

    return NovelResponse(
        id=novel_id,
        title=novel_title,
        author=author,
        language=language,
        file_hash=file_hash,
    )


@router.get("/", response_model=NovelList)
async def get_novels() -> NovelList:
    async with get_db_context() as db:
        novels = await list_novels(db)
    return NovelList(novels=novels, total=len(novels))


@router.get("/{novel_id}", response_model=NovelResponse)
async def get_novel_by_id(novel_id: int) -> NovelResponse:
    async with get_db_context() as db:
        novel = await get_novel(db, novel_id)
    if novel is None:
        raise HTTPException(status_code=404, detail="Novel not found")
    return NovelResponse(**novel)
