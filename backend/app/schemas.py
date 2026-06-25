from __future__ import annotations

from pydantic import BaseModel


class NovelCreate(BaseModel):
    title: str
    author: str = ""
    language: str = "en"


class NovelResponse(BaseModel):
    id: int
    title: str
    author: str
    language: str
    file_hash: str
    chapter_count: int = 0


class NovelList(BaseModel):
    novels: list[NovelResponse]
    total: int


class BookmarkCreate(BaseModel):
    novel_id: int
    chapter_id: int
    position: int = 0
    title: str = ""


class BookmarkResponse(BaseModel):
    id: int
    novel_id: int
    chapter_id: int
    position: int
    title: str


class BookmarkList(BaseModel):
    bookmarks: list[BookmarkResponse]
    total: int


class ProgressResponse(BaseModel):
    novel_id: int
    chapter_id: int
    position: int


class AnalysisRequest(BaseModel):
    novel_id: int
    chapter_start: int = 1
    chapter_end: int | None = None
    provider: str = "ollama"
    model: str = "llama3.2"


class AnalysisStatus(BaseModel):
    novel_id: int
    state: str
    chapters_processed: int
    chapters_total: int
    entities_count: int
    facts_count: int
    errors: list[dict[str, str]]


class EntityResponse(BaseModel):
    id: int
    novel_id: int
    name: str
    entity_type: str
    aliases: list[str]
    attributes: dict[str, object]
    source_chapter: int | None
    created_at: str = ""
    updated_at: str = ""


class EntityList(BaseModel):
    entities: list[EntityResponse]
    total: int


class FactResponse(BaseModel):
    id: int
    novel_id: int
    subject: str
    predicate: str
    object: str
    fact_type: str
    source_chapter: int


class AnalysisResult(BaseModel):
    novel_id: int
    entities: list[EntityResponse]
    facts: list[FactResponse]
    summary: str
