from fastapi import APIRouter, Depends, Query, status

from app.core.security import get_current_user
from app.permissions.dependencies import require_permission
from app.workflow.schemas import (
    WorkflowDefinitionCreate,
    WorkflowDefinitionResponse,
    WorkflowDefinitionUpdate,
    WorkflowInstanceCreate,
    WorkflowInstanceResponse,
)
from app.workflow.service import WorkflowService

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/definitions", response_model=list[WorkflowDefinitionResponse])
async def list_definitions(user=Depends(get_current_user)):
    return await WorkflowService.list_definitions(str(user.tenant_id))


@router.post("/definitions", response_model=WorkflowDefinitionResponse, status_code=status.HTTP_201_CREATED)
async def create_definition(
    data: WorkflowDefinitionCreate,
    user=Depends(require_permission("workflow", "manage")),
):
    return await WorkflowService.create_definition(str(user.tenant_id), data, str(user.id))


@router.patch("/definitions/{definition_id}", response_model=WorkflowDefinitionResponse)
async def update_definition(
    definition_id: str,
    data: WorkflowDefinitionUpdate,
    user=Depends(require_permission("workflow", "manage")),
):
    return await WorkflowService.update_definition(
        str(user.tenant_id), definition_id, data, str(user.id)
    )


@router.get("/instances", response_model=list[WorkflowInstanceResponse])
async def list_instances(
    status: str | None = Query(None),
    entity_type: str | None = Query(None),
    user=Depends(require_permission("workflow", "read")),
):
    return await WorkflowService.list_instances(str(user.tenant_id), status, entity_type)


@router.get("/instances/{instance_id}", response_model=WorkflowInstanceResponse)
async def get_instance(instance_id: str, user=Depends(require_permission("workflow", "read"))):
    return await WorkflowService.get_instance(str(user.tenant_id), instance_id)


@router.post("/instances", response_model=WorkflowInstanceResponse, status_code=status.HTTP_201_CREATED)
async def start_instance(
    data: WorkflowInstanceCreate,
    user=Depends(require_permission("workflow", "manage")),
):
    return await WorkflowService.start_instance(str(user.tenant_id), data, str(user.id))
