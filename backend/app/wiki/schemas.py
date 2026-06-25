from __future__ import annotations

from pydantic import BaseModel


class WikiGenerateRequest(BaseModel):
    novel_id: int
    entity_id: int | None = None
    title: str | None = None
    language: str = "en"
    prompt_version: str = "v1"


class WikiPageResponse(BaseModel):
    id: int
    novel_id: int
    entity_id: int | None
    title: str
    content: str
    language: str
    version: int
    source_chapters: list[int]
    prompt_version: str
    is_published: bool
    created_at: str
    updated_at: str


class WikiPageList(BaseModel):
    pages: list[WikiPageResponse]
    total: int


class WikiUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None
    is_published: bool | None = None
