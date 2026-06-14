import json

from beanie import PydanticObjectId

from app.core.redis import get_redis
from app.organization.models import OrgNode, OrgNodeType
from app.shared.exceptions import ValidationError


class OrganizationRepository:
    CACHE_PREFIX = "org:tree:"

    @staticmethod
    async def list_node_types(tenant_id: str) -> list[OrgNodeType]:
        return (
            await OrgNodeType.find({"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False})
            .sort("+code")
            .to_list()
        )

    @staticmethod
    async def get_node_type(tenant_id: str, type_id: str) -> OrgNodeType | None:
        node_type = await OrgNodeType.get(type_id)
        if node_type and str(node_type.tenant_id) == tenant_id and not node_type.is_deleted:
            return node_type
        return None

    @staticmethod
    async def get_node_type_by_code(tenant_id: str, code: str) -> OrgNodeType | None:
        return await OrgNodeType.find_one(
            {
                "tenant_id": PydanticObjectId(tenant_id),
                "code": code,
                "is_deleted": False,
            }
        )

    @staticmethod
    async def create_node_type(tenant_id: str, data: dict) -> OrgNodeType:
        node_type = OrgNodeType(tenant_id=PydanticObjectId(tenant_id), **data)
        await node_type.insert()
        return node_type

    @staticmethod
    async def update_node_type(node_type: OrgNodeType, data: dict) -> OrgNodeType:
        for key, value in data.items():
            if value is not None:
                setattr(node_type, key, value)
        await node_type.touch()
        return node_type

    @staticmethod
    async def soft_delete_node_type(node_type: OrgNodeType) -> None:
        await node_type.soft_delete()

    @staticmethod
    async def get_node(tenant_id: str, node_id: str) -> OrgNode | None:
        node = await OrgNode.get(node_id)
        if node and str(node.tenant_id) == tenant_id and not node.is_deleted:
            return node
        return None

    @staticmethod
    async def list_children(tenant_id: str, parent_id: str | None) -> list[OrgNode]:
        filt = {
            "tenant_id": PydanticObjectId(tenant_id),
            "is_deleted": False,
            "parent_id": PydanticObjectId(parent_id) if parent_id else None,
        }
        return await OrgNode.find(filt).sort("+sort_order").to_list()

    @staticmethod
    async def list_all_nodes(tenant_id: str) -> list[OrgNode]:
        return (
            await OrgNode.find({"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False})
            .sort("+sort_order")
            .to_list()
        )

    @staticmethod
    async def create_node(tenant_id: str, data: dict, parent: OrgNode | None) -> OrgNode:
        path: list[str] = []
        depth = 0
        if parent:
            path = parent.path + [str(parent.id)]
            depth = parent.depth + 1

        node = OrgNode(
            tenant_id=PydanticObjectId(tenant_id),
            parent_id=parent.id if parent else None,
            path=path,
            depth=depth,
            **data,
        )
        await node.insert()
        await OrganizationRepository.invalidate_cache(tenant_id)
        return node

    @staticmethod
    async def update_node(node: OrgNode, data: dict) -> OrgNode:
        for key, value in data.items():
            if value is not None:
                setattr(node, key, value)
        await node.touch()
        await OrganizationRepository.invalidate_cache(str(node.tenant_id))
        return node

    @staticmethod
    async def move_node(node: OrgNode, new_parent: OrgNode | None) -> OrgNode:
        if new_parent and str(new_parent.id) == str(node.id):
            raise ValidationError("Cannot move node under itself")
        if new_parent and str(node.id) in new_parent.path:
            raise ValidationError("Cannot move node under its descendant")

        if new_parent:
            node.parent_id = new_parent.id
            node.path = new_parent.path + [str(new_parent.id)]
            node.depth = new_parent.depth + 1
        else:
            node.parent_id = None
            node.path = []
            node.depth = 0

        new_path_prefix = node.path + [str(node.id)]
        await node.touch()

        descendants = await OrgNode.find(
            {
                "tenant_id": node.tenant_id,
                "is_deleted": False,
                "path": {"$all": [str(node.id)]},
            }
        ).to_list()

        for desc in descendants:
            if str(desc.id) == str(node.id):
                continue
            idx = None
            for i, seg in enumerate(desc.path):
                if seg == str(node.id):
                    idx = i
                    break
            if idx is not None:
                suffix = desc.path[idx:]
                desc.path = new_path_prefix[:-1] + suffix
                desc.depth = len(desc.path)
                await desc.touch()

        await OrganizationRepository.invalidate_cache(str(node.tenant_id))
        return node

    @staticmethod
    async def soft_delete_node(node: OrgNode) -> None:
        children = await OrganizationRepository.list_children(str(node.tenant_id), str(node.id))
        if children:
            raise ValidationError("Cannot delete node with children")
        await node.soft_delete()
        await OrganizationRepository.invalidate_cache(str(node.tenant_id))

    @staticmethod
    async def get_tree_cached(tenant_id: str) -> list[dict] | None:
        try:
            redis = await get_redis()
            cached = await redis.get(f"{OrganizationRepository.CACHE_PREFIX}{tenant_id}")
            if cached:
                return json.loads(cached)
        except Exception:
            pass
        return None

    @staticmethod
    async def set_tree_cache(tenant_id: str, tree: list[dict]) -> None:
        try:
            redis = await get_redis()
            await redis.setex(
                f"{OrganizationRepository.CACHE_PREFIX}{tenant_id}",
                300,
                json.dumps(tree),
            )
        except Exception:
            pass

    @staticmethod
    async def invalidate_cache(tenant_id: str) -> None:
        try:
            redis = await get_redis()
            await redis.delete(f"{OrganizationRepository.CACHE_PREFIX}{tenant_id}")
        except Exception:
            pass
