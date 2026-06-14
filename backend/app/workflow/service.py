from datetime import UTC, datetime

from beanie import PydanticObjectId

from app.approval.service import ApprovalService
from app.audit.service import AuditService
from app.notifications.service import NotificationService
from app.shared.exceptions import ConflictError, NotFoundError, ValidationError
from app.workflow.models import WorkflowDefinition, WorkflowInstance
from app.workflow.repository import WorkflowRepository
from app.workflow.schemas import (
    WorkflowDefinitionCreate,
    WorkflowDefinitionResponse,
    WorkflowDefinitionUpdate,
    WorkflowInstanceCreate,
    WorkflowInstanceResponse,
)


class WorkflowService:
    @staticmethod
    def _def_response(d: WorkflowDefinition) -> WorkflowDefinitionResponse:
        return WorkflowDefinitionResponse(
            id=str(d.id),
            code=d.code,
            name=d.name,
            description=d.description,
            entity_type=d.entity_type,
            steps=d.steps,
            is_active=d.is_active,
        )

    @staticmethod
    def _inst_response(i: WorkflowInstance) -> WorkflowInstanceResponse:
        return WorkflowInstanceResponse(
            id=str(i.id),
            definition_id=str(i.definition_id),
            entity_type=i.entity_type,
            entity_id=i.entity_id,
            current_step_id=i.current_step_id,
            status=i.status,
            context=i.context,
            history=i.history,
            initiated_by=str(i.initiated_by),
        )

    @staticmethod
    async def list_definitions(tenant_id: str) -> list[WorkflowDefinitionResponse]:
        defs = await WorkflowRepository.list_definitions(tenant_id)
        return [WorkflowService._def_response(d) for d in defs]

    @staticmethod
    async def create_definition(
        tenant_id: str, data: WorkflowDefinitionCreate, user_id: str
    ) -> WorkflowDefinitionResponse:
        existing = await WorkflowRepository.get_definition_by_code(tenant_id, data.code)
        if existing:
            raise ConflictError(f"Workflow '{data.code}' already exists")
        steps = [s.model_dump() for s in data.steps]
        definition = await WorkflowRepository.create_definition(
            tenant_id,
            {**data.model_dump(exclude={"steps"}), "steps": steps},
        )
        await AuditService.log_event(
            tenant_id, "workflow.definition.created", "workflow_definition", str(definition.id), user_id
        )
        return WorkflowService._def_response(definition)

    @staticmethod
    async def update_definition(
        tenant_id: str, definition_id: str, data: WorkflowDefinitionUpdate, user_id: str
    ) -> WorkflowDefinitionResponse:
        definition = await WorkflowRepository.get_definition(tenant_id, definition_id)
        if definition is None:
            raise NotFoundError("Workflow definition not found")
        update_data = data.model_dump(exclude_unset=True)
        if "steps" in update_data and update_data["steps"] is not None:
            update_data["steps"] = [s.model_dump() if hasattr(s, "model_dump") else s for s in update_data["steps"]]
        updated = await WorkflowRepository.update_definition(definition, update_data)
        await AuditService.log_event(
            tenant_id, "workflow.definition.updated", "workflow_definition", definition_id, user_id
        )
        return WorkflowService._def_response(updated)

    @staticmethod
    async def start_instance(
        tenant_id: str, data: WorkflowInstanceCreate, user_id: str
    ) -> WorkflowInstanceResponse:
        definition = await WorkflowRepository.get_definition_by_code(tenant_id, data.definition_code)
        if definition is None or not definition.is_active:
            raise NotFoundError("Workflow definition not found or inactive")
        if not definition.steps:
            raise ValidationError("Workflow has no steps")

        first_step = definition.steps[0]
        context = {**data.context, "scope_node_id": data.scope_node_id}

        instance = await WorkflowRepository.create_instance(
            tenant_id,
            {
                "definition_id": definition.id,
                "entity_type": data.entity_type,
                "entity_id": data.entity_id,
                "current_step_id": first_step["id"],
                "status": "in_progress",
                "context": context,
                "history": [
                    {
                        "step_id": first_step["id"],
                        "action": "started",
                        "by": user_id,
                        "at": datetime.now(UTC).isoformat(),
                    }
                ],
                "initiated_by": PydanticObjectId(user_id),
            },
        )

        await WorkflowService._execute_step(tenant_id, instance, definition, first_step, user_id)

        await AuditService.log_event(
            tenant_id,
            "workflow.instance.started",
            "workflow_instance",
            str(instance.id),
            user_id,
            {"definition_code": data.definition_code},
        )
        return WorkflowService._inst_response(instance)

    @staticmethod
    async def _execute_step(
        tenant_id: str,
        instance: WorkflowInstance,
        definition: WorkflowDefinition,
        step: dict,
        actor_id: str,
    ) -> None:
        step_type = step.get("type", "action")
        if step_type == "approval":
            await ApprovalService.create_from_workflow_step(
                tenant_id=tenant_id,
                workflow_instance_id=str(instance.id),
                step=step,
                requester_id=actor_id,
                context=instance.context,
            )
        elif step_type == "notification":
            recipient_id = step.get("config", {}).get("user_id", actor_id)
            await NotificationService.notify_user(
                tenant_id,
                recipient_id,
                title=step.get("config", {}).get("title", "Workflow update"),
                body=step.get("config", {}).get("body", f"Step '{step.get('name')}' reached"),
                notification_type="workflow",
                link=f"/workflows/{instance.id}",
            )
            await WorkflowService._advance_step(tenant_id, instance, definition, step, actor_id)

    @staticmethod
    async def _advance_step(
        tenant_id: str,
        instance: WorkflowInstance,
        definition: WorkflowDefinition,
        current_step: dict,
        actor_id: str,
    ) -> WorkflowInstance:
        steps = definition.steps
        current_idx = next((i for i, s in enumerate(steps) if s["id"] == current_step["id"]), -1)
        next_idx = current_idx + 1

        if next_idx >= len(steps):
            instance.status = "completed"
            instance.current_step_id = None
            instance.history.append(
                {
                    "step_id": current_step["id"],
                    "action": "completed",
                    "by": actor_id,
                    "at": datetime.now(UTC).isoformat(),
                }
            )
        else:
            next_step = steps[next_idx]
            instance.current_step_id = next_step["id"]
            instance.history.append(
                {
                    "step_id": next_step["id"],
                    "action": "entered",
                    "by": actor_id,
                    "at": datetime.now(UTC).isoformat(),
                }
            )
            await WorkflowRepository.save_instance(instance)
            await WorkflowService._execute_step(tenant_id, instance, definition, next_step, actor_id)
            return instance

        await WorkflowRepository.save_instance(instance)
        return instance

    @staticmethod
    async def on_approval_resolved(
        tenant_id: str,
        workflow_instance_id: str,
        step_id: str,
        approved: bool,
        actor_id: str,
    ) -> WorkflowInstanceResponse | None:
        instance = await WorkflowRepository.get_instance(tenant_id, workflow_instance_id)
        if instance is None:
            return None
        definition = await WorkflowRepository.get_definition(tenant_id, str(instance.definition_id))
        if definition is None:
            return None

        current_step = next((s for s in definition.steps if s["id"] == step_id), None)
        if current_step is None:
            return None

        if not approved:
            instance.status = "rejected"
            instance.history.append(
                {
                    "step_id": step_id,
                    "action": "rejected",
                    "by": actor_id,
                    "at": datetime.now(UTC).isoformat(),
                }
            )
            await WorkflowRepository.save_instance(instance)
            return WorkflowService._inst_response(instance)

        instance.history.append(
            {
                "step_id": step_id,
                "action": "approved",
                "by": actor_id,
                "at": datetime.now(UTC).isoformat(),
            }
        )
        updated = await WorkflowService._advance_step(tenant_id, instance, definition, current_step, actor_id)
        return WorkflowService._inst_response(updated)

    @staticmethod
    async def list_instances(
        tenant_id: str, status: str | None = None, entity_type: str | None = None
    ) -> list[WorkflowInstanceResponse]:
        instances = await WorkflowRepository.list_instances(tenant_id, status, entity_type)
        return [WorkflowService._inst_response(i) for i in instances]

    @staticmethod
    async def get_instance(tenant_id: str, instance_id: str) -> WorkflowInstanceResponse:
        instance = await WorkflowRepository.get_instance(tenant_id, instance_id)
        if instance is None:
            raise NotFoundError("Workflow instance not found")
        return WorkflowService._inst_response(instance)
