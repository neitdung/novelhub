from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Query

from ..database import get_db_context
from ..schemas import (
    WikiBacklinkList,
    WikiLink,
    WikiLinkList,
    WikiLintIssue,
    WikiLintReport,
)
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


@router.get("/pages/{page_id}/backlinks", response_model=WikiBacklinkList)
async def get_wiki_page_backlinks(page_id: int) -> WikiBacklinkList:
    """Return wiki pages that link to this page (share the same entity reference)."""
    page = await get_wiki_page(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Wiki page not found")

    async with get_db_context() as db:
        if page.entity_id is not None:
            cursor = await db.execute(
                "SELECT id, title, novel_id FROM wiki_pages"
                " WHERE entity_id = ? AND id != ?"
                " ORDER BY title",
                (page.entity_id, page_id),
            )
        else:
            # For pages without entity, find pages that mention the same title
            cursor = await db.execute(
                "SELECT id, title, novel_id FROM wiki_pages"
                " WHERE title LIKE ? AND id != ?"
                " ORDER BY title",
                (f"%{page.title}%", page_id),
            )
        rows = await cursor.fetchall()

    backlinks = [
        WikiLink(page_id=r[0], title=str(r[1]), novel_id=int(str(r[2])))
        for r in rows
    ]

    return WikiBacklinkList(backlinks=backlinks, total=len(backlinks))


@router.get("/pages/{page_id}/links", response_model=WikiLinkList)
async def get_wiki_page_links(page_id: int) -> WikiLinkList:
    """Return wiki pages linked from this page via entity relationships."""
    page = await get_wiki_page(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Wiki page not found")

    async with get_db_context() as db:
        if page.entity_id is not None:
            cursor = await db.execute(
                "SELECT DISTINCT wp.id, wp.title, wp.novel_id"
                " FROM entity_relationships er"
                " JOIN wiki_pages wp"
                " ON wp.entity_id IN (er.target_entity_id, er.source_entity_id)"
                " WHERE (er.source_entity_id = ? OR er.target_entity_id = ?)"
                " AND wp.id != ?"
                " AND wp.novel_id = ?"
                " ORDER BY wp.title",
                (page.entity_id, page.entity_id, page_id, page.novel_id),
            )
        else:
            cursor = await db.execute(
                "SELECT id, title, novel_id FROM wiki_pages"
                " WHERE novel_id = ? AND id != ?"
                " ORDER BY title LIMIT 50",
                (page.novel_id, page_id),
            )
        rows = await cursor.fetchall()

    links = [
        WikiLink(page_id=r[0], title=str(r[1]), novel_id=int(str(r[2])))
        for r in rows
    ]

    return WikiLinkList(links=links, total=len(links))


@router.get("/lint/{novel_id}", response_model=WikiLintReport)
async def get_wiki_lint_report(novel_id: int) -> WikiLintReport:
    """Return contradiction/orphan/coverage report for wiki pages."""
    orphan_pages: list[WikiLintIssue] = []
    contradictions: list[WikiLintIssue] = []
    coverage_issues: list[WikiLintIssue] = []

    async with get_db_context() as db:
        # Orphan pages: pages without entity_id and empty source_chapters
        cursor = await db.execute(
            "SELECT id, title, source_chapters FROM wiki_pages"
            " WHERE novel_id = ? AND (entity_id IS NULL OR entity_id = 0)"
            " ORDER BY title",
            (novel_id,),
        )
        orphan_rows = await cursor.fetchall()
        for r in orphan_rows:
            source_ch = json.loads(str(r[2])) if r[2] else []
            if not source_ch:
                orphan_pages.append(
                    WikiLintIssue(
                        issue_type="orphan",
                        page_id=int(str(r[0])),
                        title=str(r[1]),
                        description="No entity ref and no source chapters",
                        severity="medium",
                    )
                )

        # Contradictions: same entity having multiple wiki pages
        cursor = await db.execute(
            "SELECT entity_id, COUNT(*) as cnt, GROUP_CONCAT(id) as ids"
            " FROM wiki_pages"
            " WHERE novel_id = ? AND entity_id IS NOT NULL AND entity_id != 0"
            " GROUP BY entity_id"
            " HAVING cnt > 1",
            (novel_id,),
        )
        conflict_rows = await cursor.fetchall()
        for r in conflict_rows:
            ids_str = str(r[2]) if r[2] else ""
            page_ids = ids_str.split(",")

            cursor2 = await db.execute(
                "SELECT id, title FROM wiki_pages WHERE id IN"
                f" ({','.join('?' * len(page_ids))})",
                [int(pid) for pid in page_ids],
            )
            pages = list(await cursor2.fetchall())
            titles = [str(p[1]) for p in pages]

            contradictions.append(
                WikiLintIssue(
                    issue_type="contradiction",
                    page_id=int(str(pages[0][0])),
                    title=titles[0],
                    description=(
                        f"Entity has {len(page_ids)} wiki pages:"
                        f" {', '.join(titles)}"
                    ),
                    severity="high",
                )
            )

        # Coverage: entities without wiki pages
        cursor = await db.execute(
            "SELECT e.id, e.name, e.entity_type FROM entities e"
            " WHERE e.novel_id = ?"
            " AND NOT EXISTS ("
            "   SELECT 1 FROM wiki_pages wp"
            "   WHERE wp.entity_id = e.id AND wp.novel_id = e.novel_id"
            " )"
            " ORDER BY e.name LIMIT 100",
            (novel_id,),
        )
        missing_entity_rows = await cursor.fetchall()
        for r in missing_entity_rows:
            coverage_issues.append(
                WikiLintIssue(
                    issue_type="coverage",
                    page_id=0,
                    title=str(r[1]),
                    description=f"Entity '{r[1]}' (type: {r[2]}) has no wiki page",
                    severity="low",
                )
            )

    total_issues = len(orphan_pages) + len(contradictions) + len(coverage_issues)

    return WikiLintReport(
        novel_id=novel_id,
        orphan_pages=orphan_pages,
        contradictions=contradictions,
        coverage_issues=coverage_issues,
        total_issues=total_issues,
    )


@router.delete("/pages/{page_id}")
async def delete_wiki_page_endpoint(page_id: int) -> dict[str, str]:
    deleted = await delete_wiki_page(page_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Wiki page not found")
    return {"status": "deleted"}
