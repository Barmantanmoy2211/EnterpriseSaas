from fastapi import APIRouter, Depends, Query, status

from app.permissions.dependencies import require_permission
from app.project.schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from app.project.service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    status: str | None = Query(None),
    user=Depends(require_permission("project", "read")),
):
    return await ProjectService.list_projects(str(user.tenant_id), status)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, user=Depends(require_permission("project", "read"))):
    return await ProjectService.get_project(str(user.tenant_id), project_id)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    user=Depends(require_permission("project", "manage")),
):
    return await ProjectService.create_project(str(user.tenant_id), data, str(user.id))


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    user=Depends(require_permission("project", "manage")),
):
    return await ProjectService.update_project(str(user.tenant_id), project_id, data, str(user.id))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    user=Depends(require_permission("project", "manage")),
):
    await ProjectService.delete_project(str(user.tenant_id), project_id, str(user.id))
