from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import Settings
from .database import check_db_health
from .routers import (
    analysis,
    backup,
    bookmarks,
    chapters,
    chat,
    export,
    graph,
    kb,
    novels,
    search,
    sources,
    wiki,
)
from .ws import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.settings = Settings()
    yield


app = FastAPI(
    title="NovelHub",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(novels.router)
app.include_router(bookmarks.router)
app.include_router(analysis.router)
app.include_router(kb.router)
app.include_router(search.router)
app.include_router(wiki.router)
app.include_router(chat.router)
app.include_router(graph.router)
app.include_router(export.router)
app.include_router(backup.router)
app.include_router(sources.router)
app.include_router(chapters.router)
app.include_router(ws_router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    db_status = await check_db_health()
    return {"status": "ok", **db_status}
