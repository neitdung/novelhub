from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from ..export import export_novel_json, export_novel_markdown, export_wiki_markdown

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/novel/{novel_id}/markdown")
async def export_novel_markdown_endpoint(novel_id: int) -> HTMLResponse:
    try:
        content = await export_novel_markdown(novel_id)
        return HTMLResponse(content=content)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/novel/{novel_id}/json")
async def export_novel_json_endpoint(novel_id: int) -> JSONResponse:
    try:
        data = await export_novel_json(novel_id)
        return JSONResponse(content=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/novel/{novel_id}/wiki/markdown")
async def export_wiki_markdown_endpoint(novel_id: int) -> HTMLResponse:
    try:
        content = await export_wiki_markdown(novel_id)
        return HTMLResponse(content=content)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
