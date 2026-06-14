from beanie import PydanticObjectId

from app.project.models import Project


class ProjectRepository:
    @staticmethod
    async def list_all(tenant_id: str, status: str | None = None) -> list[Project]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if status:
            filt["status"] = status
        return await Project.find(filt).sort("-created_at").to_list()

    @staticmethod
    async def get(tenant_id: str, project_id: str) -> Project | None:
        project = await Project.get(project_id)
        if project and str(project.tenant_id) == tenant_id and not project.is_deleted:
            return project
        return None

    @staticmethod
    async def get_by_code(tenant_id: str, code: str) -> Project | None:
        return await Project.find_one(
            {"tenant_id": PydanticObjectId(tenant_id), "code": code, "is_deleted": False}
        )

    @staticmethod
    async def create(tenant_id: str, data: dict) -> Project:
        project = Project(tenant_id=PydanticObjectId(tenant_id), **data)
        await project.insert()
        return project

    @staticmethod
    async def update(project: Project, data: dict) -> Project:
        for key, value in data.items():
            if value is not None:
                setattr(project, key, value)
        await project.touch()
        return project

    @staticmethod
    async def soft_delete(project: Project) -> None:
        await project.soft_delete()
