from beanie import PydanticObjectId

from app.resource.models import Resource, ResourceAllocation


class ResourceRepository:
    @staticmethod
    async def list_resources(tenant_id: str, resource_type: str | None = None) -> list[Resource]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if resource_type:
            filt["resource_type"] = resource_type
        return await Resource.find(filt).sort("+name").to_list()

    @staticmethod
    async def get_resource(tenant_id: str, resource_id: str) -> Resource | None:
        resource = await Resource.get(resource_id)
        if resource and str(resource.tenant_id) == tenant_id and not resource.is_deleted:
            return resource
        return None

    @staticmethod
    async def create_resource(tenant_id: str, data: dict) -> Resource:
        resource = Resource(tenant_id=PydanticObjectId(tenant_id), **data)
        await resource.insert()
        return resource

    @staticmethod
    async def update_resource(resource: Resource, data: dict) -> Resource:
        for key, value in data.items():
            if value is not None:
                setattr(resource, key, value)
        await resource.touch()
        return resource

    @staticmethod
    async def soft_delete_resource(resource: Resource) -> None:
        await resource.soft_delete()

    @staticmethod
    async def list_allocations(tenant_id: str, resource_id: str | None = None) -> list[ResourceAllocation]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if resource_id:
            filt["resource_id"] = PydanticObjectId(resource_id)
        return await ResourceAllocation.find(filt).sort("-start_date").to_list()

    @staticmethod
    async def create_allocation(tenant_id: str, data: dict) -> ResourceAllocation:
        allocation = ResourceAllocation(tenant_id=PydanticObjectId(tenant_id), **data)
        await allocation.insert()
        return allocation
