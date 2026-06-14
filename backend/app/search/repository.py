from beanie import PydanticObjectId

from app.search.models import SearchDocument


class SearchRepository:
    @staticmethod
    async def upsert(
        tenant_id: str,
        entity_type: str,
        entity_id: str,
        title: str,
        body: str = "",
        keywords: list[str] | None = None,
        metadata: dict | None = None,
    ) -> SearchDocument:
        existing = await SearchDocument.find_one(
            {
                "tenant_id": PydanticObjectId(tenant_id),
                "entity_type": entity_type,
                "entity_id": entity_id,
                "is_deleted": False,
            }
        )
        if existing:
            existing.title = title
            existing.body = body
            existing.keywords = keywords or []
            existing.metadata = metadata or {}
            await existing.touch()
            return existing

        doc = SearchDocument(
            tenant_id=PydanticObjectId(tenant_id),
            entity_type=entity_type,
            entity_id=entity_id,
            title=title,
            body=body,
            keywords=keywords or [],
            metadata=metadata or {},
        )
        await doc.insert()
        return doc

    @staticmethod
    async def search(tenant_id: str, query: str, limit: int = 20) -> list[SearchDocument]:
        if not query.strip():
            return []

        try:
            return (
                await SearchDocument.find(
                    {
                        "tenant_id": PydanticObjectId(tenant_id),
                        "is_deleted": False,
                        "$text": {"$search": query},
                    }
                )
                .limit(limit)
                .to_list()
            )
        except Exception:
            regex = {"$regex": query, "$options": "i"}
            return (
                await SearchDocument.find(
                    {
                        "tenant_id": PydanticObjectId(tenant_id),
                        "is_deleted": False,
                        "$or": [
                            {"title": regex},
                            {"body": regex},
                            {"keywords": regex},
                        ],
                    }
                )
                .limit(limit)
                .to_list()
            )

    @staticmethod
    async def remove(tenant_id: str, entity_type: str, entity_id: str) -> None:
        doc = await SearchDocument.find_one(
            {
                "tenant_id": PydanticObjectId(tenant_id),
                "entity_type": entity_type,
                "entity_id": entity_id,
                "is_deleted": False,
            }
        )
        if doc:
            await doc.soft_delete()
