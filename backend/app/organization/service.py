from app.organization.models import OrgNode, OrgNodeType
from app.organization.repository import OrganizationRepository
from app.organization.schemas import (
    OrgNodeCreate,
    OrgNodeMove,
    OrgNodeResponse,
    OrgNodeTypeCreate,
    OrgNodeTypeResponse,
    OrgNodeTypeUpdate,
    OrgNodeUpdate,
)
from app.shared.exceptions import ConflictError, NotFoundError, ValidationError


class OrganizationService:
    @staticmethod
    def _node_type_response(nt: OrgNodeType) -> OrgNodeTypeResponse:
        return OrgNodeTypeResponse(
            id=str(nt.id),
            code=nt.code,
            label=nt.label,
            allowed_child_types=nt.allowed_child_types,
            type_schema=nt.type_schema,
            is_root_allowed=nt.is_root_allowed,
        )

    @staticmethod
    def _node_response(node: OrgNode, children: list[OrgNodeResponse] | None = None) -> OrgNodeResponse:
        return OrgNodeResponse(
            id=str(node.id),
            parent_id=str(node.parent_id) if node.parent_id else None,
            node_type=node.node_type,
            name=node.name,
            metadata=node.metadata,
            path=node.path,
            depth=node.depth,
            sort_order=node.sort_order,
            children=children or [],
        )

    @staticmethod
    async def list_node_types(tenant_id: str) -> list[OrgNodeTypeResponse]:
        types = await OrganizationRepository.list_node_types(tenant_id)
        return [OrganizationService._node_type_response(t) for t in types]

    @staticmethod
    async def create_node_type(tenant_id: str, data: OrgNodeTypeCreate) -> OrgNodeTypeResponse:
        existing = await OrganizationRepository.get_node_type_by_code(tenant_id, data.code)
        if existing:
            raise ConflictError(f"Node type '{data.code}' already exists")
        nt = await OrganizationRepository.create_node_type(tenant_id, data.model_dump())
        return OrganizationService._node_type_response(nt)

    @staticmethod
    async def update_node_type(tenant_id: str, type_id: str, data: OrgNodeTypeUpdate) -> OrgNodeTypeResponse:
        nt = await OrganizationRepository.get_node_type(tenant_id, type_id)
        if nt is None:
            raise NotFoundError("Node type not found")
        updated = await OrganizationRepository.update_node_type(nt, data.model_dump(exclude_unset=True))
        return OrganizationService._node_type_response(updated)

    @staticmethod
    async def delete_node_type(tenant_id: str, type_id: str) -> None:
        nt = await OrganizationRepository.get_node_type(tenant_id, type_id)
        if nt is None:
            raise NotFoundError("Node type not found")
        in_use = await OrganizationRepository.count_nodes_using_type(tenant_id, nt.code)
        if in_use > 0:
            raise ValidationError(
                f"Cannot delete level type '{nt.code}' — {in_use} hierarchy node(s) still use it"
            )
        await OrganizationRepository.soft_delete_node_type(nt)

    @staticmethod
    async def _validate_node_type(tenant_id: str, node_type_code: str, parent: OrgNode | None) -> OrgNodeType:
        node_type = await OrganizationRepository.get_node_type_by_code(tenant_id, node_type_code)
        if node_type is None:
            raise ValidationError(f"Unknown node type: {node_type_code}")

        if parent is None:
            if not node_type.is_root_allowed:
                raise ValidationError(f"Node type '{node_type_code}' cannot be used at root level")
        else:
            parent_type = await OrganizationRepository.get_node_type_by_code(tenant_id, parent.node_type)
            if parent_type is None:
                raise ValidationError("Parent node type not found")
            if node_type_code not in parent_type.allowed_child_types:
                raise ValidationError(
                    f"Node type '{node_type_code}' not allowed under '{parent.node_type}'"
                )
        return node_type

    @staticmethod
    async def create_node(tenant_id: str, data: OrgNodeCreate) -> OrgNodeResponse:
        parent = None
        if data.parent_id:
            parent = await OrganizationRepository.get_node(tenant_id, data.parent_id)
            if parent is None:
                raise NotFoundError("Parent node not found")

        await OrganizationService._validate_node_type(tenant_id, data.node_type, parent)
        node = await OrganizationRepository.create_node(
            tenant_id,
            data.model_dump(exclude={"parent_id"}),
            parent,
        )
        from app.search.service import SearchService

        await SearchService.index_org_node(tenant_id, node)
        return OrganizationService._node_response(node)

    @staticmethod
    async def update_node(tenant_id: str, node_id: str, data: OrgNodeUpdate) -> OrgNodeResponse:
        node = await OrganizationRepository.get_node(tenant_id, node_id)
        if node is None:
            raise NotFoundError("Node not found")
        updated = await OrganizationRepository.update_node(node, data.model_dump(exclude_unset=True))
        return OrganizationService._node_response(updated)

    @staticmethod
    async def move_node(tenant_id: str, node_id: str, data: OrgNodeMove) -> OrgNodeResponse:
        node = await OrganizationRepository.get_node(tenant_id, node_id)
        if node is None:
            raise NotFoundError("Node not found")

        new_parent = None
        if data.parent_id:
            new_parent = await OrganizationRepository.get_node(tenant_id, data.parent_id)
            if new_parent is None:
                raise NotFoundError("Parent node not found")

        await OrganizationService._validate_node_type(tenant_id, node.node_type, new_parent)
        moved = await OrganizationRepository.move_node(node, new_parent)
        return OrganizationService._node_response(moved)

    @staticmethod
    async def delete_node(tenant_id: str, node_id: str) -> None:
        node = await OrganizationRepository.get_node(tenant_id, node_id)
        if node is None:
            raise NotFoundError("Node not found")
        await OrganizationRepository.soft_delete_node(node)

    @staticmethod
    def _build_tree(nodes: list[OrgNode]) -> list[OrgNodeResponse]:
        by_parent: dict[str | None, list[OrgNode]] = {}
        for node in nodes:
            key = str(node.parent_id) if node.parent_id else None
            by_parent.setdefault(key, []).append(node)

        def build(parent_key: str | None) -> list[OrgNodeResponse]:
            result = []
            for node in sorted(by_parent.get(parent_key, []), key=lambda n: n.sort_order):
                children = build(str(node.id))
                result.append(OrganizationService._node_response(node, children))
            return result

        return build(None)

    @staticmethod
    async def get_tree(tenant_id: str) -> list[OrgNodeResponse]:
        cached = await OrganizationRepository.get_tree_cached(tenant_id)
        if cached is not None:
            return [OrgNodeResponse(**item) for item in cached]

        nodes = await OrganizationRepository.list_all_nodes(tenant_id)
        tree = OrganizationService._build_tree(nodes)
        await OrganizationRepository.set_tree_cache(
            tenant_id, [t.model_dump() for t in tree]
        )
        return tree
