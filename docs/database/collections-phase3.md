# Phase 3 — Operations Collections

MongoDB collections for Projects, Tasks, Calendar, Documents, Communication, Reports, and Analytics.

## projects

| Field | Type | Notes |
|-------|------|-------|
| tenant_id | ObjectId | Tenant isolation |
| name | string | Project name |
| description | string | |
| code | string | Unique per tenant |
| status | string | active, on_hold, completed, cancelled |
| priority | string | low, medium, high |
| owner_id | ObjectId? | User reference |
| org_node_id | ObjectId? | Org scope |
| start_date | date? | |
| end_date | date? | |
| metadata | object | Extensible fields |

## tasks

| Field | Type | Notes |
|-------|------|-------|
| tenant_id | ObjectId | |
| title | string | |
| description | string | |
| project_id | ObjectId? | Optional project link |
| assignee_id | ObjectId? | User reference |
| created_by | ObjectId | |
| status | string | todo, in_progress, done, cancelled |
| priority | string | |
| due_date | date? | |
| tags | string[] | |
| metadata | object | |

## calendar_events

| Field | Type | Notes |
|-------|------|-------|
| tenant_id | ObjectId | |
| title | string | |
| start_at | datetime | |
| end_at | datetime | |
| organizer_id | ObjectId | |
| attendee_ids | ObjectId[] | |
| location | string | |
| all_day | boolean | |
| related_entity_type | string | Optional link |
| related_entity_id | string | |

## documents

| Field | Type | Notes |
|-------|------|-------|
| tenant_id | ObjectId | |
| title | string | |
| file_url | string | S3/external URL (upload deferred) |
| mime_type | string | |
| size_bytes | int | |
| folder_path | string | Virtual folder |
| uploaded_by | ObjectId | |
| tags | string[] | |
| version | int | Incremented on file change |

## communication_messages

| Field | Type | Notes |
|-------|------|-------|
| tenant_id | ObjectId | |
| message_type | string | announcement, message |
| subject | string | |
| body | string | |
| sender_id | ObjectId | |
| recipient_id | ObjectId? | Direct messages only |
| channel | string | general, hr, ops, etc. |
| is_pinned | boolean | |
| read_by | ObjectId[] | Read receipts |

## saved_reports

| Field | Type | Notes |
|-------|------|-------|
| tenant_id | ObjectId | |
| name | string | |
| entity_type | string | employee, project, task |
| filters | object | MongoDB filter dict |
| columns | string[] | Output columns |
| created_by | ObjectId | |
| is_shared | boolean | |

## report_runs

| Field | Type | Notes |
|-------|------|-------|
| tenant_id | ObjectId | |
| report_id | ObjectId | |
| run_by | ObjectId | |
| row_count | int | |
| result_preview | object[] | First 20 rows |
| run_at | datetime | |

## Analytics

No dedicated collection — aggregated at query time from employees, projects, tasks, recruitment, and approvals.
