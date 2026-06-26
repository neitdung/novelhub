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


# --- External Source Ingestion Models ---

class SourceCreate(BaseModel):
    name: str
    url_template: str
    css_selector: str = ".txtnav"
    language: str = "zh"
    active: bool = True


class SourceUpdate(BaseModel):
    name: str | None = None
    url_template: str | None = None
    css_selector: str | None = None
    language: str | None = None
    active: bool | None = None


class SourceResponse(BaseModel):
    id: int
    name: str
    url_template: str
    css_selector: str
    language: str
    active: bool
    created_at: str = ""
    updated_at: str = ""


class SourceList(BaseModel):
    sources: list[SourceResponse]
    total: int


class ImportRequest(BaseModel):
    source_id: int
    chapter_start: int = 1
    chapter_end: int | None = None
    url_template_params: dict[str, str] = {}


class ImportJobResponse(BaseModel):
    id: int
    novel_id: int
    source_id: int
    chapter_start: int
    chapter_end: int
    status: str
    progress: int
    error: str | None = None
    created_at: str = ""


class ImportStatusResponse(BaseModel):
    id: int
    status: str
    progress: int
    error: str | None = None


class ChapterResponse(BaseModel):
    id: int
    novel_id: int
    chapter_number: int
    title: str
    content: str | None = None
    raw_content: str | None = None
    source_url: str | None = None
    is_corrected: bool = False
    corrected_at: str | None = None
    created_at: str = ""


class ChapterListResponse(BaseModel):
    chapters: list[ChapterResponse]
    total: int


class ChapterUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    raw_content: str | None = None


class BatchChapterUpdate(BaseModel):
    updates: list[ChapterUpdate]
    chapter_ids: list[int]


class BatchDeleteRequest(BaseModel):
    chapter_ids: list[int] | None = None
    chapter_start: int | None = None
    chapter_end: int | None = None


class ChapterSwapRequest(BaseModel):
    chapter_id_a: int
    chapter_id_b: int


class TxtImportResponse(BaseModel):
    novel_id: int
    chapters_created: int
    title: str
