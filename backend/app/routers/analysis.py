from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..analysis.pipeline import AnalysisPipeline, PipelineState
from ..database import get_db_context
from ..llm import FakeLLMProvider
from ..schemas import AnalysisRequest, AnalysisStatus

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

pipelines: dict[int, AnalysisPipeline] = {}


@router.post("/start", response_model=AnalysisStatus)
async def start_analysis(request: AnalysisRequest) -> AnalysisStatus:
    async with get_db_context() as db:
        cursor = await db.execute(
            "SELECT id FROM novels WHERE id = ?", (request.novel_id,)
        )
        novel = await cursor.fetchone()
        if not novel:
            raise HTTPException(status_code=404, detail="Novel not found")

        cursor = await db.execute(
            "SELECT chapter_number, title, content FROM chapters"
            " WHERE novel_id = ? AND chapter_number >= ?"
            " ORDER BY chapter_number",
            (request.novel_id, request.chapter_start),
        )
        chapters = await cursor.fetchall()

    if not chapters:
        raise HTTPException(
            status_code=400, detail="No chapters found for analysis"
        )

    llm = FakeLLMProvider()
    pipeline = AnalysisPipeline(llm, max_concurrent=1)
    pipelines[request.novel_id] = pipeline

    chapter_data = [
        {
            "chapter_number": ch[0],
            "title": ch[1] or f"Chapter {ch[0]}",
            "content": ch[2] or "",
        }
        for ch in chapters
    ]

    import asyncio

    asyncio.create_task(
        pipeline.analyze_chapters(request.novel_id, chapter_data)
    )

    return AnalysisStatus(
        novel_id=request.novel_id,
        state=PipelineState.RUNNING.value,
        chapters_processed=0,
        chapters_total=len(list(chapters)),
        entities_count=0,
        facts_count=0,
        errors=[],
    )


@router.get("/{novel_id}/status", response_model=AnalysisStatus)
async def get_analysis_status(novel_id: int) -> AnalysisStatus:
    pipeline = pipelines.get(novel_id)
    if not pipeline:
        raise HTTPException(
            status_code=404, detail="No analysis found for this novel"
        )

    status = pipeline.get_status()
    entities = []
    facts = []
    for task in pipeline.tasks.values():
        if task.extraction:
            entities.extend(task.extraction.entities)
            facts.extend(task.extraction.facts)

    return AnalysisStatus(
        novel_id=novel_id,
        state=status["state"],
        chapters_processed=len(
            [t for t in pipeline.tasks.values() if t.extraction]
        ),
        chapters_total=len(pipeline.tasks),
        entities_count=len(entities),
        facts_count=len(facts),
        errors=[
            {"chapter": str(e["chapter"]), "error": e["error"]}
            for e in status.get("errors", [])
        ],
    )


@router.post("/{novel_id}/pause")
async def pause_analysis(novel_id: int) -> dict[str, str]:
    pipeline = pipelines.get(novel_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="No analysis found")
    pipeline.pause()
    return {"status": "paused"}


@router.post("/{novel_id}/resume")
async def resume_analysis(novel_id: int) -> dict[str, str]:
    pipeline = pipelines.get(novel_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="No analysis found")
    pipeline.resume()
    return {"status": "resumed"}


@router.post("/{novel_id}/cancel")
async def cancel_analysis(novel_id: int) -> dict[str, str]:
    pipeline = pipelines.get(novel_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="No analysis found")
    pipeline.cancel()
    return {"status": "cancelled"}
