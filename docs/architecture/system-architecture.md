# EnterpriseOS System Architecture

## Overview

EnterpriseOS is a metadata-driven, multi-tenant SaaS platform built with Domain-Driven Design (DDD) and Clean Architecture principles. The platform provides reusable enterprise services; business modules consume these services rather than reimplementing them.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation                          │
│              Next.js App Router (Frontend)               │
├─────────────────────────────────────────────────────────┤
│                    API Layer                             │
│              FastAPI Routers + Schemas                   │
├─────────────────────────────────────────────────────────┤
│                 Application Layer                        │
│              Services (Business Logic)                   │
├─────────────────────────────────────────────────────────┤
│                   Domain Layer                           │
│              Models, Events, Validators                  │
├─────────────────────────────────────────────────────────┤
│               Infrastructure Layer                       │
│     Repositories, MongoDB, Redis, S3, Celery            │
└─────────────────────────────────────────────────────────┘
```

## Request Flow

1. Client sends request with `Authorization: Bearer <token>` and optional `X-Tenant-Slug`
2. Middleware assigns request ID and resolves tenant context
3. JWT validated; `tenant_id` extracted and set in context
4. Permission dependency checks RBAC before protected endpoints
5. Service layer executes business logic via repositories
6. Response returned with consistent error envelope on failure

## Multi-Tenancy

- Every document includes `tenant_id`
- Repository queries always filter by `tenant_id`
- JWT embeds `tenant_id`; cross-tenant access returns 403
- Tenant registration creates isolated data partition

## Module Communication

- Modules expose service interfaces
- Cross-module calls go through services, not direct model imports
- Domain events (Phase 1b) will decouple async side effects

## Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js 15, React, TypeScript, Tailwind, shadcn/ui |
| Backend | FastAPI, Pydantic v2, Beanie ODM |
| Database | MongoDB |
| Cache | Redis |
| Queue | Celery + Redis |
| Storage | AWS S3 (Phase 2) |

## Phase 1 Scope

- Authentication (register, login, refresh, logout)
- Tenant management and settings
- Metadata-driven organization hierarchy
- RBAC permission engine with hierarchy-scoped assignments

## Deferred (Phase 1b+)

- Workflow engine, notifications, audit log, Atlas Search
- HR and operations modules (Phase 2+)
- AI assistant (Phase 5)
