from beanie import PydanticObjectId

from app.approval.models import ApprovalRequest
from app.approval.repository import ApprovalRepository
from app.approval.schemas import ApprovalCreate, ApprovalResponse
from app.audit.service import AuditService
from app.notifications.service import NotificationService
from app.shared.exceptions import ForbiddenError, NotFoundError, ValidationError


class ApprovalService:
    @staticmethod
    def _to_response(a: ApprovalRequest) -> ApprovalResponse:
        return ApprovalResponse(
            id=str(a.id),
            workflow_instance_id=str(a.workflow_instance_id) if a.workflow_instance_id else None,
            step_id=a.step_id,
            requester_id=str(a.requester_id),
            approver_id=str(a.approver_id) if a.approver_id else None,
            scope_node_id=str(a.scope_node_id) if a.scope_node_id else None,
            title=a.title,
            description=a.description,
            status=a.status,
            comments=a.comments,
            entity_type=a.entity_type,
            entity_id=a.entity_id,
            created_at=a.created_at.isoformat(),
        )

    @staticmethod
    async def _resolve_approver(
        tenant_id: str,
        step_config: dict,
        context: dict,
    ) -> str | None:
        if step_config.get("approver_user_id"):
            return step_config["approver_user_id"]
        if step_config.get("approver_role_id"):
            from app.permissions.repository import PermissionRepository

            role_id = step_config["approver_role_id"]
            assignments = await PermissionRepository.list_assignments(tenant_id)
            scope_node_id = context.get("scope_node_id")
            for assignment in assignments:
                if str(assignment.role_id) == role_id:
                    if scope_node_id and assignment.scope_node_id:
                        if str(assignment.scope_node_id) == scope_node_id:
                            return str(assignment.user_id)
                    elif assignment.scope_node_id is None:
                        return str(assignment.user_id)
        return step_config.get("fallback_approver_id")

    @staticmethod
    async def create_from_workflow_step(
        tenant_id: str,
        workflow_instance_id: str,
        step: dict,
        requester_id: str,
        context: dict,
    ) -> ApprovalResponse:
        config = step.get("config", {})
        approver_id = await ApprovalService._resolve_approver(tenant_id, config, context)
        if not approver_id:
            raise ValidationError(f"No approver resolved for step '{step.get('name')}'")

        approval = await ApprovalRepository.create(
            tenant_id,
            {
                "workflow_instance_id": PydanticObjectId(workflow_instance_id),
                "step_id": step["id"],
                "requester_id": PydanticObjectId(requester_id),
                "approver_id": PydanticObjectId(approver_id),
                "scope_node_id": PydanticObjectId(context["scope_node_id"])
                if context.get("scope_node_id")
                else None,
                "title": config.get("title", f"Approval: {step.get('name')}"),
                "description": config.get("description", ""),
                "entity_type": context.get("entity_type", ""),
                "entity_id": context.get("entity_id", ""),
            },
        )

        await NotificationService.notify_user(
            tenant_id,
            approver_id,
            title="Approval required",
            body=approval.title,
            notification_type="approval",
            link=f"/approvals/{approval.id}",
        )

        return ApprovalService._to_response(approval)

    @staticmethod
    async def create_manual(
        tenant_id: str, data: ApprovalCreate, requester_id: str
    ) -> ApprovalResponse:
        approval = await ApprovalRepository.create(
            tenant_id,
            {
                "requester_id": PydanticObjectId(requester_id),
                "approver_id": PydanticObjectId(data.approver_id),
                "scope_node_id": PydanticObjectId(data.scope_node_id)
                if data.scope_node_id
                else None,
                "title": data.title,
                "description": data.description,
                "entity_type": data.entity_type,
                "entity_id": data.entity_id,
            },
        )
        await NotificationService.notify_user(
            tenant_id,
            data.approver_id,
            title="Approval required",
            body=data.title,
            notification_type="approval",
            link=f"/approvals/{approval.id}",
        )
        await AuditService.log_event(
            tenant_id, "approval.created", "approval", str(approval.id), requester_id
        )
        return ApprovalService._to_response(approval)

    @staticmethod
    async def approve(
        tenant_id: str, approval_id: str, actor_id: str, comments: str = ""
    ) -> ApprovalResponse:
        return await ApprovalService._resolve(tenant_id, approval_id, actor_id, "approved", comments)

    @staticmethod
    async def reject(
        tenant_id: str, approval_id: str, actor_id: str, comments: str = ""
    ) -> ApprovalResponse:
        return await ApprovalService._resolve(tenant_id, approval_id, actor_id, "rejected", comments)

    @staticmethod
    async def _resolve(
        tenant_id: str, approval_id: str, actor_id: str, status: str, comments: str
    ) -> ApprovalResponse:
        approval = await ApprovalRepository.get(tenant_id, approval_id)
        if approval is None:
            raise NotFoundError("Approval not found")
        if approval.status != "pending":
            raise ValidationError("Approval already resolved")
        if str(approval.approver_id) != actor_id:
            raise ForbiddenError("You are not the assigned approver")

        updated = await ApprovalRepository.resolve(approval, status, actor_id, comments)

        await NotificationService.notify_user(
            tenant_id,
            str(approval.requester_id),
            title=f"Approval {status}",
            body=f"Your request '{approval.title}' was {status}",
            notification_type="approval",
        )

        if approval.workflow_instance_id and approval.step_id:
            from app.workflow.service import WorkflowService

            await WorkflowService.on_approval_resolved(
                tenant_id,
                str(approval.workflow_instance_id),
                approval.step_id,
                approved=(status == "approved"),
                actor_id=actor_id,
            )

        await AuditService.log_event(
            tenant_id,
            f"approval.{status}",
            "approval",
            approval_id,
            actor_id,
            {"comments": comments},
        )
        return ApprovalService._to_response(updated)

    @staticmethod
    async def list_pending(tenant_id: str, user_id: str) -> list[ApprovalResponse]:
        items = await ApprovalRepository.list_pending_for_approver(tenant_id, user_id)
        return [ApprovalService._to_response(a) for a in items]

    @staticmethod
    async def list_mine(tenant_id: str, user_id: str) -> list[ApprovalResponse]:
        items = await ApprovalRepository.list_for_requester(tenant_id, user_id)
        return [ApprovalService._to_response(a) for a in items]

    @staticmethod
    async def list_all(tenant_id: str, status: str | None = None) -> list[ApprovalResponse]:
        items = await ApprovalRepository.list_all(tenant_id, status)
        return [ApprovalService._to_response(a) for a in items]

    @staticmethod
    async def get(tenant_id: str, approval_id: str) -> ApprovalResponse:
        approval = await ApprovalRepository.get(tenant_id, approval_id)
        if approval is None:
            raise NotFoundError("Approval not found")
        return ApprovalService._to_response(approval)
