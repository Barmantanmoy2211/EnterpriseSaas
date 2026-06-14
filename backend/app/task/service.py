from beanie import PydanticObjectId

from app.audit.service import AuditService
from app.search.repository import SearchRepository
from app.shared.exceptions import NotFoundError
from app.task.models import Task
from app.task.repository import TaskRepository
from app.task.schemas import TaskCreate, TaskResponse, TaskUpdate


class TaskService:
    @staticmethod
    def _response(task: Task) -> TaskResponse:
        return TaskResponse(
            id=str(task.id),
            title=task.title,
            description=task.description,
            project_id=str(task.project_id) if task.project_id else None,
            assignee_id=str(task.assignee_id) if task.assignee_id else None,
            created_by=str(task.created_by),
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            tags=task.tags,
            metadata=task.metadata,
        )

    @staticmethod
    async def _index(task: Task) -> None:
        await SearchRepository.upsert(
            str(task.tenant_id),
            "task",
            str(task.id),
            task.title,
            task.description,
            task.tags + [task.status, task.priority],
            {"status": task.status, "project_id": str(task.project_id) if task.project_id else ""},
        )

    @staticmethod
    async def list_tasks(
        tenant_id: str,
        project_id: str | None = None,
        assignee_id: str | None = None,
        status: str | None = None,
    ) -> list[TaskResponse]:
        tasks = await TaskRepository.list_all(tenant_id, project_id, assignee_id, status)
        return [TaskService._response(t) for t in tasks]

    @staticmethod
    async def get_task(tenant_id: str, task_id: str) -> TaskResponse:
        task = await TaskRepository.get(tenant_id, task_id)
        if task is None:
            raise NotFoundError("Task not found")
        return TaskService._response(task)

    @staticmethod
    async def create_task(tenant_id: str, data: TaskCreate, actor_id: str) -> TaskResponse:
        payload = data.model_dump(exclude={"project_id", "assignee_id"})
        payload["created_by"] = PydanticObjectId(actor_id)
        if data.project_id:
            payload["project_id"] = PydanticObjectId(data.project_id)
        if data.assignee_id:
            payload["assignee_id"] = PydanticObjectId(data.assignee_id)

        task = await TaskRepository.create(tenant_id, payload)
        await TaskService._index(task)
        await AuditService.log_event(tenant_id, "task.created", "task", str(task.id), actor_id)
        return TaskService._response(task)

    @staticmethod
    async def update_task(
        tenant_id: str, task_id: str, data: TaskUpdate, actor_id: str
    ) -> TaskResponse:
        task = await TaskRepository.get(tenant_id, task_id)
        if task is None:
            raise NotFoundError("Task not found")

        updates = data.model_dump(exclude_unset=True, exclude={"project_id", "assignee_id"})
        if data.project_id is not None:
            updates["project_id"] = PydanticObjectId(data.project_id) if data.project_id else None
        if data.assignee_id is not None:
            updates["assignee_id"] = PydanticObjectId(data.assignee_id) if data.assignee_id else None

        task = await TaskRepository.update(task, updates)
        await TaskService._index(task)
        await AuditService.log_event(tenant_id, "task.updated", "task", str(task.id), actor_id)
        return TaskService._response(task)

    @staticmethod
    async def delete_task(tenant_id: str, task_id: str, actor_id: str) -> None:
        task = await TaskRepository.get(tenant_id, task_id)
        if task is None:
            raise NotFoundError("Task not found")
        await TaskRepository.soft_delete(task)
        await AuditService.log_event(tenant_id, "task.deleted", "task", str(task.id), actor_id)
