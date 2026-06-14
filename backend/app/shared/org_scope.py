"""Hierarchy scope helpers for visibility filtering."""

from beanie import PydanticObjectId

from app.organization.repository import OrganizationRepository
from app.permissions.repository import PermissionRepository
from app.permissions.service import PermissionService


async def user_has_global_scope(tenant_id: str, user_id: str) -> bool:
    roles = await PermissionService.get_roles_for_user(tenant_id, user_id)
    if any(r.code == "tenant_admin" for r in roles):
        return True
    assignments = await PermissionRepository.list_assignments(tenant_id, user_id)
    return any(a.scope_node_id is None for a in assignments)


async def get_visible_org_node_ids(tenant_id: str, user_id: str) -> set[str] | None:
    """
    Return None if the user can see all org nodes (tenant admin or global assignment).
    Otherwise return the set of org node ids in scope (assigned node + descendants).
    """
    if await user_has_global_scope(tenant_id, user_id):
        return None

    assignments = await PermissionRepository.list_assignments(tenant_id, user_id)
    scope_roots = [str(a.scope_node_id) for a in assignments if a.scope_node_id]
    if not scope_roots:
        return set()

    visible: set[str] = set()
    all_nodes = await OrganizationRepository.list_all_nodes(tenant_id)
    children_by_parent: dict[str | None, list] = {}
    for node in all_nodes:
        key = str(node.parent_id) if node.parent_id else None
        children_by_parent.setdefault(key, []).append(node)

    def collect_subtree(root_id: str) -> None:
        visible.add(root_id)
        for child in children_by_parent.get(root_id, []):
            collect_subtree(str(child.id))

    for root_id in scope_roots:
        collect_subtree(root_id)

    return visible


def record_in_org_scope(
  org_node_id: str | None,
  visible_ids: set[str] | None,
) -> bool:
    """True if record is visible under the user's org scope."""
    if visible_ids is None:
        return True
    if org_node_id is None:
        return False
    return org_node_id in visible_ids
