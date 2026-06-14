# Role & Permission Matrix — Phase 1

## System Roles

| Role Code | Name | Scope | Description |
|-----------|------|-------|-------------|
| tenant_admin | Tenant Administrator | Global | Full access; seeded on registration |

## System Permissions

| Resource | Action | Description | Default Roles |
|----------|--------|-------------|---------------|
| org | read | View organization structure | tenant_admin |
| org | create | Create organization nodes | tenant_admin |
| org | update | Update/move organization nodes | tenant_admin |
| org | delete | Delete organization nodes | tenant_admin |
| org | manage_types | Configure node types | tenant_admin |
| user | read | View users | tenant_admin |
| user | manage | Create/update users | tenant_admin |
| role | read | View roles and assignments | tenant_admin |
| role | manage | Create roles and assign | tenant_admin |
| tenant | settings | Update tenant settings | tenant_admin |
| audit | read | View audit logs | tenant_admin |
| notification | read | View own notifications | tenant_admin |
| notification | manage | Send notifications | tenant_admin |
| workflow | read | View workflows and instances | tenant_admin |
| workflow | manage | Create workflows and start instances | tenant_admin |
| approval | read | View all approval requests | tenant_admin |
| approval | action | Approve or reject requests | tenant_admin |
| search | read | Use global search | tenant_admin |
| search | manage | Reindex search documents | tenant_admin |

## Scope Model

- **Global scope** (`scope_node_id = null`): Permission applies tenant-wide
- **Node scope** (`scope_node_id = <node_id>`): Permission applies to node and descendants (Phase 1b full evaluation)

## ABAC Conditions (Phase 1)

Permissions may include a `conditions` object. Phase 1 evaluates simple equality checks against request context:

```json
{ "owner_id": "<user_id>" }
```

## Custom Roles

Tenants can create custom roles via `POST /api/v1/permissions/roles` with selected `permission_ids`. System roles cannot have permissions modified via API.
