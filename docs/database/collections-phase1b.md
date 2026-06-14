# MongoDB Collections — Phase 1b Additions

## audit_logs

Immutable append-only audit trail.

| Field | Type | Description |
|-------|------|-------------|
| tenant_id | ObjectId | Tenant scope |
| user_id | ObjectId | Actor (nullable for system) |
| action | string | e.g. auth.login, approval.approved |
| resource_type | string | Entity type |
| resource_id | string | Entity ID |
| details | object | Additional context |
| ip_address | string | Client IP |
| request_id | string | Correlation ID |
| created_at | datetime | Event timestamp |

## notifications

| Field | Type | Description |
|-------|------|-------------|
| tenant_id | ObjectId | |
| user_id | ObjectId | Recipient |
| title | string | |
| body | string | |
| notification_type | string | info, approval, workflow, system |
| is_read | boolean | |
| link | string | Deep link URL |
| metadata | object | |

## workflow_definitions

| Field | Type | Description |
|-------|------|-------------|
| tenant_id | ObjectId | |
| code | string | Unique workflow code |
| name | string | |
| entity_type | string | leave_request, generic_request, etc. |
| steps | array | Step definitions with type and config |
| is_active | boolean | |

## workflow_instances

| Field | Type | Description |
|-------|------|-------------|
| tenant_id | ObjectId | |
| definition_id | ObjectId | |
| entity_type | string | |
| entity_id | string | |
| current_step_id | string | |
| status | string | pending, in_progress, completed, rejected |
| context | object | Runtime context |
| history | array | Step history |
| initiated_by | ObjectId | |

## approval_requests

| Field | Type | Description |
|-------|------|-------------|
| tenant_id | ObjectId | |
| workflow_instance_id | ObjectId | Optional link to workflow |
| step_id | string | Workflow step |
| requester_id | ObjectId | |
| approver_id | ObjectId | Resolved approver |
| scope_node_id | ObjectId | Hierarchy scope |
| title | string | |
| status | string | pending, approved, rejected |
| comments | string | |

## search_documents

| Field | Type | Description |
|-------|------|-------------|
| tenant_id | ObjectId | |
| entity_type | string | org_node, user, etc. |
| entity_id | string | |
| title | string | Searchable title |
| body | string | Searchable body |
| keywords | array | Additional terms |
| metadata | object | |

Text index on `title`, `body`, `keywords`.
