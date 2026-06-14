from datetime import UTC, date, datetime

from beanie import PydanticObjectId

from app.attendance.models import AttendanceRecord, LeaveRequest, LeaveType
from app.attendance.repository import AttendanceRepository, LeaveRepository
from app.attendance.schemas import (
    AttendanceCreate,
    AttendanceResponse,
    LeaveRequestCreate,
    LeaveRequestResponse,
    LeaveTypeCreate,
    LeaveTypeResponse,
)
from app.audit.service import AuditService
from app.shared.exceptions import ConflictError, NotFoundError


class AttendanceService:
    @staticmethod
    def _attendance(r: AttendanceRecord) -> AttendanceResponse:
        return AttendanceResponse(
            id=str(r.id),
            employee_id=str(r.employee_id),
            date=r.date,
            check_in=r.check_in,
            check_out=r.check_out,
            status=r.status,
            notes=r.notes,
            hours_worked=r.hours_worked,
        )

    @staticmethod
    async def list_records(
        tenant_id: str, employee_id: str | None = None, from_date: date | None = None
    ) -> list[AttendanceResponse]:
        records = await AttendanceRepository.list_records(tenant_id, employee_id, from_date)
        return [AttendanceService._attendance(r) for r in records]

    @staticmethod
    async def check_in(tenant_id: str, employee_id: str, actor_id: str) -> AttendanceResponse:
        today = date.today()
        existing = await AttendanceRepository.get_by_employee_date(tenant_id, employee_id, today)
        if existing and existing.check_in:
            raise ConflictError("Already checked in today")
        if existing:
            existing.check_in = datetime.now(UTC)
            existing.status = "present"
            await existing.touch()
            record = existing
        else:
            record = await AttendanceRepository.create_record(
                tenant_id,
                {
                    "employee_id": PydanticObjectId(employee_id),
                    "date": today,
                    "check_in": datetime.now(UTC),
                    "status": "present",
                },
            )
        await AuditService.log_event(
            tenant_id, "attendance.check_in", "attendance", str(record.id), actor_id
        )
        return AttendanceService._attendance(record)

    @staticmethod
    async def check_out(tenant_id: str, employee_id: str, actor_id: str) -> AttendanceResponse:
        today = date.today()
        record = await AttendanceRepository.get_by_employee_date(tenant_id, employee_id, today)
        if record is None or not record.check_in:
            raise NotFoundError("No check-in found for today")
        if record.check_out:
            raise ConflictError("Already checked out today")
        record.check_out = datetime.now(UTC)
        delta = record.check_out - record.check_in
        record.hours_worked = round(delta.total_seconds() / 3600, 2)
        await record.touch()
        await AuditService.log_event(
            tenant_id, "attendance.check_out", "attendance", str(record.id), actor_id
        )
        return AttendanceService._attendance(record)

    @staticmethod
    async def create_record(
        tenant_id: str, data: AttendanceCreate, actor_id: str
    ) -> AttendanceResponse:
        record = await AttendanceRepository.create_record(
            tenant_id,
            {
                "employee_id": PydanticObjectId(data.employee_id),
                "date": data.date,
                "status": data.status,
                "notes": data.notes,
            },
        )
        return AttendanceService._attendance(record)


class LeaveService:
    @staticmethod
    def _type(t: LeaveType) -> LeaveTypeResponse:
        return LeaveTypeResponse(
            id=str(t.id), code=t.code, name=t.name, days_allowed=t.days_allowed, is_paid=t.is_paid
        )

    @staticmethod
    def _request(r: LeaveRequest) -> LeaveRequestResponse:
        return LeaveRequestResponse(
            id=str(r.id),
            employee_id=str(r.employee_id),
            leave_type_id=str(r.leave_type_id),
            start_date=r.start_date,
            end_date=r.end_date,
            days=r.days,
            reason=r.reason,
            status=r.status,
            workflow_instance_id=str(r.workflow_instance_id) if r.workflow_instance_id else None,
        )

    @staticmethod
    async def list_types(tenant_id: str) -> list[LeaveTypeResponse]:
        types = await LeaveRepository.list_types(tenant_id)
        return [LeaveService._type(t) for t in types]

    @staticmethod
    async def create_type(tenant_id: str, data: LeaveTypeCreate, actor_id: str) -> LeaveTypeResponse:
        t = await LeaveRepository.create_type(tenant_id, data.model_dump())
        return LeaveService._type(t)

    @staticmethod
    async def list_requests(
        tenant_id: str, employee_id: str | None = None, status: str | None = None
    ) -> list[LeaveRequestResponse]:
        requests = await LeaveRepository.list_requests(tenant_id, employee_id, status)
        return [LeaveService._request(r) for r in requests]

    @staticmethod
    async def create_request(
        tenant_id: str, data: LeaveRequestCreate, actor_id: str
    ) -> LeaveRequestResponse:
        leave_type = await LeaveRepository.get_type(tenant_id, data.leave_type_id)
        if leave_type is None:
            raise NotFoundError("Leave type not found")

        req = await LeaveRepository.create_request(
            tenant_id,
            {
                "employee_id": PydanticObjectId(data.employee_id),
                "leave_type_id": PydanticObjectId(data.leave_type_id),
                "start_date": data.start_date,
                "end_date": data.end_date,
                "days": data.days,
                "reason": data.reason,
            },
        )

        if data.start_workflow:
            from app.workflow.schemas import WorkflowInstanceCreate
            from app.workflow.service import WorkflowService

            try:
                instance = await WorkflowService.start_instance(
                    tenant_id,
                    WorkflowInstanceCreate(
                        definition_code="leave_approval",
                        entity_type="leave_request",
                        entity_id=str(req.id),
                        context={
                            "entity_type": "leave_request",
                            "entity_id": str(req.id),
                            "employee_id": data.employee_id,
                        },
                        scope_node_id=data.scope_node_id,
                    ),
                    actor_id,
                )
                req.workflow_instance_id = PydanticObjectId(instance.id)
                await req.touch()
            except NotFoundError:
                pass

        await AuditService.log_event(
            tenant_id, "leave.requested", "leave_request", str(req.id), actor_id
        )
        return LeaveService._request(req)

    @staticmethod
    async def update_status(
        tenant_id: str, request_id: str, status: str, actor_id: str
    ) -> LeaveRequestResponse:
        req = await LeaveRepository.get_request(tenant_id, request_id)
        if req is None:
            raise NotFoundError("Leave request not found")
        updated = await LeaveRepository.update_request(
            req, {"status": status, "approved_by": PydanticObjectId(actor_id)}
        )
        return LeaveService._request(updated)
