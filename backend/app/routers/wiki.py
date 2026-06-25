from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ..wiki.generator import (
    delete_wiki_page,
    generate_wiki,
    get_wiki_page,
    list_wiki_pages,
)
from ..wiki.schemas import WikiGenerateRequest, WikiPageList, WikiPageResponse

router = APIRouter(prefix="/api/wiki", tags=["wiki"])


@router.post("/generate", response_model=WikiPageResponse, status_code=201)
async def generate_wiki_endpoint(
    request: WikiGenerateRequest,
) -> WikiPageResponse:
    try:
        return await generate_wiki(request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/pages", response_model=WikiPageList)
async def list_wiki_pages_endpoint(
    novel_id: int,
    entity_id: int | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> WikiPageList:
    pages, total = await list_wiki_pages(novel_id, entity_id, limit, offset)
    return WikiPageList(pages=pages, total=total)


@router.get("/pages/{page_id}", response_model=WikiPageResponse)
async def get_wiki_page_endpoint(page_id: int) -> WikiPageResponse:
    page = await get_wiki_page(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Wiki page not found")
    return page


@router.delete("/pages/{page_id}")
async def delete_wiki_page_endpoint(page_id: int) -> dict[str, str]:
    deleted = await delete_wiki_page(page_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Wiki page not found")
    return {"status": "deleted"}
