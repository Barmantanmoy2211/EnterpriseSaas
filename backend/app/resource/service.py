from beanie import PydanticObjectId

from app.audit.service import AuditService
from app.resource.models import Resource
from app.resource.repository import ResourceRepository
from app.resource.schemas import (
    AllocationCreate,
    AllocationResponse,
    ResourceCreate,
    ResourceResponse,
    ResourceUpdate,
)
from app.search.repository import SearchRepository
from app.shared.exceptions import NotFoundError


class ResourceService:
    @staticmethod
    def _resource_response(resource: Resource) -> ResourceResponse:
        return ResourceResponse(
            id=str(resource.id),
            name=resource.name,
            resource_type=resource.resource_type,
            description=resource.description,
            capacity=resource.capacity,
            capacity_unit=resource.capacity_unit,
            status=resource.status,
            org_node_id=str(resource.org_node_id) if resource.org_node_id else None,
            metadata=resource.metadata,
        )

    @staticmethod
    async def _index(resource: Resource) -> None:
        await SearchRepository.upsert(
            str(resource.tenant_id),
            "resource",
            str(resource.id),
            resource.name,
            resource.description,
            [resource.resource_type, resource.status],
            {"capacity": resource.capacity},
        )

    @staticmethod
    async def list_resources(
        tenant_id: str, resource_type: str | None = None
    ) -> list[ResourceResponse]:
        resources = await ResourceRepository.list_resources(tenant_id, resource_type)
        return [ResourceService._resource_response(r) for r in resources]

    @staticmethod
    async def get_resource(tenant_id: str, resource_id: str) -> ResourceResponse:
        resource = await ResourceRepository.get_resource(tenant_id, resource_id)
        if resource is None:
            raise NotFoundError("Resource not found")
        return ResourceService._resource_response(resource)

    @staticmethod
    async def create_resource(tenant_id: str, data: ResourceCreate, actor_id: str) -> ResourceResponse:
        payload = data.model_dump(exclude={"org_node_id"})
        if data.org_node_id:
            payload["org_node_id"] = PydanticObjectId(data.org_node_id)
        resource = await ResourceRepository.create_resource(tenant_id, payload)
        await ResourceService._index(resource)
        await AuditService.log_event(tenant_id, "resource.created", "resource", str(resource.id), actor_id)
        return ResourceService._resource_response(resource)

    @staticmethod
    async def update_resource(
        tenant_id: str, resource_id: str, data: ResourceUpdate, actor_id: str
    ) -> ResourceResponse:
        resource = await ResourceRepository.get_resource(tenant_id, resource_id)
        if resource is None:
            raise NotFoundError("Resource not found")
        updates = data.model_dump(exclude_unset=True, exclude={"org_node_id"})
        if data.org_node_id is not None:
            updates["org_node_id"] = PydanticObjectId(data.org_node_id) if data.org_node_id else None
        resource = await ResourceRepository.update_resource(resource, updates)
        await ResourceService._index(resource)
        await AuditService.log_event(tenant_id, "resource.updated", "resource", str(resource.id), actor_id)
        return ResourceService._resource_response(resource)

    @staticmethod
    async def delete_resource(tenant_id: str, resource_id: str, actor_id: str) -> None:
        resource = await ResourceRepository.get_resource(tenant_id, resource_id)
        if resource is None:
            raise NotFoundError("Resource not found")
        await ResourceRepository.soft_delete_resource(resource)
        await AuditService.log_event(tenant_id, "resource.deleted", "resource", str(resource.id), actor_id)

    @staticmethod
    async def list_allocations(
        tenant_id: str, resource_id: str | None = None
    ) -> list[AllocationResponse]:
        allocations = await ResourceRepository.list_allocations(tenant_id, resource_id)
        return [
            AllocationResponse(
                id=str(a.id),
                resource_id=str(a.resource_id),
                project_id=str(a.project_id) if a.project_id else None,
                allocated_units=a.allocated_units,
                start_date=a.start_date,
                end_date=a.end_date,
                notes=a.notes,
                allocated_by=str(a.allocated_by),
            )
            for a in allocations
        ]

    @staticmethod
    async def create_allocation(
        tenant_id: str, data: AllocationCreate, actor_id: str
    ) -> AllocationResponse:
        resource = await ResourceRepository.get_resource(tenant_id, data.resource_id)
        if resource is None:
            raise NotFoundError("Resource not found")

        payload = data.model_dump(exclude={"resource_id", "project_id"})
        payload["resource_id"] = PydanticObjectId(data.resource_id)
        payload["allocated_by"] = PydanticObjectId(actor_id)
        if data.project_id:
            payload["project_id"] = PydanticObjectId(data.project_id)

        allocation = await ResourceRepository.create_allocation(tenant_id, payload)
        await AuditService.log_event(
            tenant_id, "resource.allocated", "resource_allocation", str(allocation.id), actor_id
        )
        return AllocationResponse(
            id=str(allocation.id),
            resource_id=str(allocation.resource_id),
            project_id=str(allocation.project_id) if allocation.project_id else None,
            allocated_units=allocation.allocated_units,
            start_date=allocation.start_date,
            end_date=allocation.end_date,
            notes=allocation.notes,
            allocated_by=str(allocation.allocated_by),
        )
