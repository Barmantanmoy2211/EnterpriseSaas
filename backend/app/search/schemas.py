from typing import Any

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    entity_type: str
    entity_id: str
    title: str
    body: str
    metadata: dict[str, Any]


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int


class IndexDocumentRequest(BaseModel):
    entity_type: str
    entity_id: str
    title: str
    body: str = ""
    keywords: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
