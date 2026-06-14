# EnterpriseOS Development Roadmap

## Phase 0 — Planning (Lite)

- [x] System architecture
- [x] MongoDB collection design
- [x] Phase 1 API specification
- [x] Permission matrix

## Phase 1 — Foundation

- [x] Authentication (register, login, refresh, logout)
- [x] Multi-tenancy with tenant isolation
- [x] Organization builder (metadata-driven hierarchy)
- [x] Permission engine (RBAC)
- [x] Dashboard shell and web UI

## Phase 1b — Platform Services (Current)

- [x] Workflow engine (definitions, instances, step execution)
- [x] Approval engine (hierarchy-aware, workflow-linked)
- [x] Notification engine (in-app + Celery email stub)
- [x] Audit logging (immutable event stream)
- [x] Global search (MongoDB text index + regex fallback)
- [x] Frontend: notifications bell, search bar, workflows, approvals, audit pages

## Phase 2 — HR Platform

- Recruitment (ATS)
- Employee management
- Attendance, Leave, Performance
- Training, Onboarding, Exit

## Phase 3 — Operations

- Projects, Tasks, Calendar
- Documents, Communication
- Reports, Analytics

## Phase 4 — Enterprise Modules

- Inventory, Resources, Finance
- Procurement, Manufacturing, Logistics

## Phase 5 — AI

- Enterprise search, Chat assistant
- Predictive analytics, Smart reports, Automation

## Phase 6 — Production

- Security hardening, Performance optimization
- Monitoring, Logging, CI/CD, AWS deployment
