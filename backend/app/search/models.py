from typing import Any

from pydantic import Field

from app.shared.base_model import TenantDocument


class SearchDocument(TenantDocument):
    entity_type: str
    entity_id: str
    title: str
    body: str = ""
    keywords: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "search_documents"
        indexes = [
            [("tenant_id", 1), ("entity_type", 1), ("entity_id", 1)],
            [
                ("title", "text"),
                ("body", "text"),
                ("keywords", "text"),
            ],
        ]
