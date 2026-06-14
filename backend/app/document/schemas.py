from typing import Any

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    title: str
    description: str = ""
    file_url: str = ""
    mime_type: str = "application/octet-stream"
    size_bytes: int = 0
    folder_path: str = "/"
    tags: list[str] = Field(default_factory=list)
    related_entity_type: str = ""
    related_entity_id: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    file_url: str | None = None
    mime_type: str | None = None
    size_bytes: int | None = None
    folder_path: str | None = None
    tags: list[str] | None = None
    related_entity_type: str | None = None
    related_entity_id: str | None = None
    metadata: dict[str, Any] | None = None


class DocumentResponse(BaseModel):
    id: str
    title: str
    description: str
    file_url: str
    mime_type: str
    size_bytes: int
    folder_path: str
    uploaded_by: str
    tags: list[str]
    related_entity_type: str
    related_entity_id: str
    version: int
    metadata: dict[str, Any]
