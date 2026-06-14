from beanie import PydanticObjectId

from app.workflow.models import WorkflowDefinition, WorkflowInstance


class WorkflowRepository:
    @staticmethod
    async def list_definitions(tenant_id: str) -> list[WorkflowDefinition]:
        return await WorkflowDefinition.find(
            {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        ).to_list()

    @staticmethod
    async def get_definition(tenant_id: str, definition_id: str) -> WorkflowDefinition | None:
        d = await WorkflowDefinition.get(definition_id)
        if d and str(d.tenant_id) == tenant_id and not d.is_deleted:
            return d
        return None

    @staticmethod
    async def get_definition_by_code(tenant_id: str, code: str) -> WorkflowDefinition | None:
        return await WorkflowDefinition.find_one(
            {
                "tenant_id": PydanticObjectId(tenant_id),
                "code": code,
                "is_deleted": False,
            }
        )

    @staticmethod
    async def create_definition(tenant_id: str, data: dict) -> WorkflowDefinition:
        definition = WorkflowDefinition(tenant_id=PydanticObjectId(tenant_id), **data)
        await definition.insert()
        return definition

    @staticmethod
    async def update_definition(defn: WorkflowDefinition, data: dict) -> WorkflowDefinition:
        for key, value in data.items():
            if value is not None:
                setattr(defn, key, value)
        await defn.touch()
        return defn

    @staticmethod
    async def create_instance(tenant_id: str, data: dict) -> WorkflowInstance:
        instance = WorkflowInstance(tenant_id=PydanticObjectId(tenant_id), **data)
        await instance.insert()
        return instance

    @staticmethod
    async def get_instance(tenant_id: str, instance_id: str) -> WorkflowInstance | None:
        inst = await WorkflowInstance.get(instance_id)
        if inst and str(inst.tenant_id) == tenant_id and not inst.is_deleted:
            return inst
        return None

    @staticmethod
    async def list_instances(
        tenant_id: str,
        status: str | None = None,
        entity_type: str | None = None,
    ) -> list[WorkflowInstance]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if status:
            filt["status"] = status
        if entity_type:
            filt["entity_type"] = entity_type
        return await WorkflowInstance.find(filt).sort("-created_at").to_list()

    @staticmethod
    async def save_instance(instance: WorkflowInstance) -> WorkflowInstance:
        await instance.touch()
        return instance
