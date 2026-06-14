from beanie import PydanticObjectId

from app.auth.models import User
from app.organization.models import OrgNode
from app.search.repository import SearchRepository
from app.search.schemas import IndexDocumentRequest, SearchResponse, SearchResult


class SearchService:
    @staticmethod
    async def index(tenant_id: str, data: IndexDocumentRequest) -> SearchResult:
        doc = await SearchRepository.upsert(
            tenant_id,
            data.entity_type,
            data.entity_id,
            data.title,
            data.body,
            data.keywords,
            data.metadata,
        )
        return SearchResult(
            entity_type=doc.entity_type,
            entity_id=doc.entity_id,
            title=doc.title,
            body=doc.body,
            metadata=doc.metadata,
        )

    @staticmethod
    async def search(tenant_id: str, query: str, limit: int = 20) -> SearchResponse:
        docs = await SearchRepository.search(tenant_id, query, limit)
        results = [
            SearchResult(
                entity_type=d.entity_type,
                entity_id=d.entity_id,
                title=d.title,
                body=d.body,
                metadata=d.metadata,
            )
            for d in docs
        ]
        return SearchResponse(query=query, results=results, total=len(results))

    @staticmethod
    async def reindex_tenant(tenant_id: str) -> int:
        count = 0
        tenant_oid = PydanticObjectId(tenant_id)

        nodes = await OrgNode.find({"tenant_id": tenant_oid, "is_deleted": False}).to_list()
        for node in nodes:
            await SearchRepository.upsert(
                tenant_id,
                "org_node",
                str(node.id),
                node.name,
                f"{node.node_type} organization node",
                [node.node_type, node.name],
                {"depth": node.depth},
            )
            count += 1

        users = await User.find({"tenant_id": tenant_oid, "is_deleted": False}).to_list()
        for user in users:
            name = f"{user.first_name} {user.last_name}".strip() or user.email
            await SearchRepository.upsert(
                tenant_id,
                "user",
                str(user.id),
                name,
                user.email,
                [user.email, user.first_name, user.last_name],
            )
            count += 1

        return count

    @staticmethod
    async def index_org_node(tenant_id: str, node: OrgNode) -> None:
        await SearchRepository.upsert(
            tenant_id,
            "org_node",
            str(node.id),
            node.name,
            f"{node.node_type} organization node",
            [node.node_type, node.name],
            {"depth": node.depth},
        )
