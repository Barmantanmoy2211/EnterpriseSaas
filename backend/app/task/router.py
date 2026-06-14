from fastapi import APIRouter, Depends, Query, status

from app.permissions.dependencies import require_permission
from app.task.schemas import TaskCreate, TaskResponse, TaskUpdate
from app.task.service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    project_id: str | None = Query(None),
    assignee_id: str | None = Query(None),
    status: str | None = Query(None),
    user=Depends(require_permission("task", "read")),
):
    return await TaskService.list_tasks(
        str(user.tenant_id), project_id, assignee_id, status
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, user=Depends(require_permission("task", "read"))):
    return await TaskService.get_task(str(user.tenant_id), task_id)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    user=Depends(require_permission("task", "manage")),
):
    return await TaskService.create_task(str(user.tenant_id), data, str(user.id))


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    data: TaskUpdate,
    user=Depends(require_permission("task", "manage")),
):
    return await TaskService.update_task(str(user.tenant_id), task_id, data, str(user.id))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    user=Depends(require_permission("task", "manage")),
):
    await TaskService.delete_task(str(user.tenant_id), task_id, str(user.id))
