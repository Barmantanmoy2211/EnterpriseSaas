# EnterpriseOS

A metadata-driven, multi-tenant enterprise platform. HR is one module—the platform provides reusable services for authentication, hierarchy management, permissions, workflows, and more.

## Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15, React, TypeScript, Tailwind, shadcn/ui |
| Backend | Python 3.12+, FastAPI, Beanie ODM, Motor |
| Database | MongoDB |
| Cache / Queue | Redis, Celery |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (local frontend dev)
- Python 3.12+ (local backend dev)

### With Docker

```bash
cp .env.example .env
docker compose up --build
```

- **Web:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Local Development

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
EnterpriseSaas/
├── docs/           # Architecture, API specs, collections
├── backend/        # FastAPI application
├── frontend/       # Next.js application
└── docker-compose.yml
```

## Phase 1 Features

- Multi-tenant registration and authentication
- Metadata-driven organization hierarchy (unlimited depth)
- RBAC + ABAC-ready permission engine
- Dashboard shell and organization builder UI

## Phase 1b Features

- Workflow engine (definitions + instances)
- Hierarchy-aware approval engine
- In-app notifications + Celery email tasks
- Immutable audit logging
- Global search across org nodes and users

## License

Proprietary — All rights reserved.
