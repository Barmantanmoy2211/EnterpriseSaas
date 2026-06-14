from typing import Any

from beanie import PydanticObjectId
from pydantic import Field

from app.shared.base_model import TenantDocument


class Document(TenantDocument):
    title: str
    description: str = ""
    file_url: str = ""
    mime_type: str = "application/octet-stream"
    size_bytes: int = 0
    folder_path: str = "/"
    uploaded_by: PydanticObjectId
    tags: list[str] = Field(default_factory=list)
    related_entity_type: str = ""
    related_entity_id: str = ""
    version: int = 1
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "documents"
        indexes = [
            [("tenant_id", 1), ("folder_path", 1)],
            [("tenant_id", 1), ("uploaded_by", 1)],
        ]
