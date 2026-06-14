# MongoDB Collections — Phase 1

All tenant-scoped collections include `tenant_id`, `created_at`, `updated_at`, `is_deleted`, `deleted_at`.

## tenants

| Field | Type | Description |
|-------|------|-------------|
| slug | string | Unique URL-safe identifier |
| name | string | Display name |
| status | string | active, suspended |
| plan | string | starter, pro, enterprise |

**Indexes:** `slug` (unique), `status`

## tenant_settings

| Field | Type | Description |
|-------|------|-------------|
| tenant_id | ObjectId | FK to tenants |
| branding | object | primary_color, logo_url |
| auth_policy | object | Password policies |
| org_defaults | object | Default node types |

**Indexes:** `tenant_id` (unique)

## users

| Field | Type | Description |
|-------|------|-------------|
| tenant_id | ObjectId | Tenant scope |
| email | string | Login email |
| password_hash | string | bcrypt hash |
| first_name | string | |
| last_name | string | |
| status | string | active, inactive |
| profile | object | Extended profile data |

**Indexes:** `{tenant_id, email}` (unique), `{tenant_id, status}`

## refresh_tokens

| Field | Type | Description |
|-------|------|-------------|
| tenant_id | ObjectId | |
| user_id | ObjectId | |
| token_hash | string | SHA-256 of refresh token |
| expires_at | datetime | |
| revoked | boolean | |

**Indexes:** `{tenant_id, user_id}`, `token_hash`

## org_node_types

| Field | Type | Description |
|-------|------|-------------|
| tenant_id | ObjectId | |
| code | string | Machine identifier (e.g. division) |
| label | string | Display name |
| allowed_child_types | array | Valid child type codes |
| schema | object | Custom field definitions |
| is_root_allowed | boolean | Can exist at tree root |

**Indexes:** `{tenant_id, code}` (unique)

## org_nodes

| Field | Type | Description |
|-------|------|-------------|
| tenant_id | ObjectId | |
| parent_id | ObjectId | null for root nodes |
| node_type | string | References org_node_types.code |
| name | string | Display name |
| metadata | object | Custom attributes |
| path | array | Ancestor IDs for efficient queries |
| depth | int | Tree depth (0 = root) |
| sort_order | int | Sibling ordering |

**Indexes:** `{tenant_id, parent_id}`, `{tenant_id, path}`, `{tenant_id, node_type}`

## roles

| Field | Type | Description |
|-------|------|-------------|
| tenant_id | ObjectId | |
| code | string | Machine identifier |
| name | string | Display name |
| description | string | |
| is_system | boolean | Protected system role |
| permission_ids | array | ObjectId references |

**Indexes:** `{tenant_id, code}` (unique)

## permissions

| Field | Type | Description |
|-------|------|-------------|
| tenant_id | ObjectId | |
| resource | string | e.g. org, user, role |
| action | string | e.g. read, create, manage |
| description | string | |
| conditions | object | ABAC conditions (Phase 1 basic) |

**Indexes:** `{tenant_id, resource, action}` (unique)

## role_assignments

| Field | Type | Description |
|-------|------|-------------|
| tenant_id | ObjectId | |
| user_id | ObjectId | |
| role_id | ObjectId | |
| scope_node_id | ObjectId | null = global scope |

**Indexes:** `{tenant_id, user_id}`, `{tenant_id, role_id}`
