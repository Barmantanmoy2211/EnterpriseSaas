from beanie import PydanticObjectId

from app.task.models import Task


class TaskRepository:
    @staticmethod
    async def list_all(
        tenant_id: str,
        project_id: str | None = None,
        assignee_id: str | None = None,
        status: str | None = None,
    ) -> list[Task]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if project_id:
            filt["project_id"] = PydanticObjectId(project_id)
        if assignee_id:
            filt["assignee_id"] = PydanticObjectId(assignee_id)
        if status:
            filt["status"] = status
        return await Task.find(filt).sort("-created_at").to_list()

    @staticmethod
    async def get(tenant_id: str, task_id: str) -> Task | None:
        task = await Task.get(task_id)
        if task and str(task.tenant_id) == tenant_id and not task.is_deleted:
            return task
        return None

    @staticmethod
    async def create(tenant_id: str, data: dict) -> Task:
        task = Task(tenant_id=PydanticObjectId(tenant_id), **data)
        await task.insert()
        return task

    @staticmethod
    async def update(task: Task, data: dict) -> Task:
        for key, value in data.items():
            if value is not None:
                setattr(task, key, value)
        await task.touch()
        return task

    @staticmethod
    async def soft_delete(task: Task) -> None:
        await task.soft_delete()

    @staticmethod
    async def count_by_status(tenant_id: str) -> dict[str, int]:
        pipeline = [
            {"$match": {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        ]
        results = await Task.aggregate(pipeline).to_list()
        return {r["_id"]: r["count"] for r in results}
