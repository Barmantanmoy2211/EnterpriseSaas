from beanie import PydanticObjectId

from app.audit.service import AuditService
from app.project.models import Project
from app.project.repository import ProjectRepository
from app.project.schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from app.search.repository import SearchRepository
from app.shared.exceptions import ConflictError, NotFoundError


class ProjectService:
    @staticmethod
    def _response(project: Project) -> ProjectResponse:
        return ProjectResponse(
            id=str(project.id),
            name=project.name,
            description=project.description,
            code=project.code,
            status=project.status,
            priority=project.priority,
            owner_id=str(project.owner_id) if project.owner_id else None,
            org_node_id=str(project.org_node_id) if project.org_node_id else None,
            start_date=project.start_date,
            end_date=project.end_date,
            metadata=project.metadata,
        )

    @staticmethod
    async def _index(project: Project) -> None:
        await SearchRepository.upsert(
            str(project.tenant_id),
            "project",
            str(project.id),
            project.name,
            project.description,
            [project.code, project.status],
            {"status": project.status, "priority": project.priority},
        )

    @staticmethod
    async def list_projects(tenant_id: str, status: str | None = None) -> list[ProjectResponse]:
        projects = await ProjectRepository.list_all(tenant_id, status)
        return [ProjectService._response(p) for p in projects]

    @staticmethod
    async def get_project(tenant_id: str, project_id: str) -> ProjectResponse:
        project = await ProjectRepository.get(tenant_id, project_id)
        if project is None:
            raise NotFoundError("Project not found")
        return ProjectService._response(project)

    @staticmethod
    async def create_project(tenant_id: str, data: ProjectCreate, actor_id: str) -> ProjectResponse:
        if data.code:
            existing = await ProjectRepository.get_by_code(tenant_id, data.code)
            if existing:
                raise ConflictError(f"Project code '{data.code}' already exists")

        payload = data.model_dump(exclude={"owner_id", "org_node_id"})
        if data.owner_id:
            payload["owner_id"] = PydanticObjectId(data.owner_id)
        if data.org_node_id:
            payload["org_node_id"] = PydanticObjectId(data.org_node_id)

        project = await ProjectRepository.create(tenant_id, payload)
        await ProjectService._index(project)
        await AuditService.log_event(tenant_id, "project.created", "project", str(project.id), actor_id)
        return ProjectService._response(project)

    @staticmethod
    async def update_project(
        tenant_id: str, project_id: str, data: ProjectUpdate, actor_id: str
    ) -> ProjectResponse:
        project = await ProjectRepository.get(tenant_id, project_id)
        if project is None:
            raise NotFoundError("Project not found")

        updates = data.model_dump(exclude_unset=True, exclude={"owner_id", "org_node_id"})
        if data.owner_id is not None:
            updates["owner_id"] = PydanticObjectId(data.owner_id) if data.owner_id else None
        if data.org_node_id is not None:
            updates["org_node_id"] = PydanticObjectId(data.org_node_id) if data.org_node_id else None

        project = await ProjectRepository.update(project, updates)
        await ProjectService._index(project)
        await AuditService.log_event(tenant_id, "project.updated", "project", str(project.id), actor_id)
        return ProjectService._response(project)

    @staticmethod
    async def delete_project(tenant_id: str, project_id: str, actor_id: str) -> None:
        project = await ProjectRepository.get(tenant_id, project_id)
        if project is None:
            raise NotFoundError("Project not found")
        await ProjectRepository.soft_delete(project)
        await AuditService.log_event(tenant_id, "project.deleted", "project", str(project.id), actor_id)
