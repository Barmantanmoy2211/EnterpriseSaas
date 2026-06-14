from dataclasses import dataclass, field

from beanie import PydanticObjectId

from app.organization.service import OrganizationService


@dataclass
class FakeOrgNode:
    id: PydanticObjectId
    tenant_id: PydanticObjectId
    parent_id: PydanticObjectId | None
    node_type: str
    name: str
    metadata: dict = field(default_factory=dict)
    path: list[str] = field(default_factory=list)
    depth: int = 0
    sort_order: int = 0


class TestOrgTreeBuilder:
    def test_build_tree_empty(self):
        assert OrganizationService._build_tree([]) == []

    def test_build_tree_nested(self):
        tenant_id = PydanticObjectId()
        root_id = PydanticObjectId()
        child_id = PydanticObjectId()
        root = FakeOrgNode(
            id=root_id,
            tenant_id=tenant_id,
            parent_id=None,
            node_type="company",
            name="Root",
            depth=0,
            sort_order=0,
        )
        child = FakeOrgNode(
            id=child_id,
            tenant_id=tenant_id,
            parent_id=root_id,
            node_type="division",
            name="Child",
            path=[str(root_id)],
            depth=1,
            sort_order=0,
        )
        tree = OrganizationService._build_tree([root, child])  # type: ignore[arg-type]
        assert len(tree) == 1
        assert tree[0].name == "Root"
        assert len(tree[0].children) == 1
        assert tree[0].children[0].name == "Child"
