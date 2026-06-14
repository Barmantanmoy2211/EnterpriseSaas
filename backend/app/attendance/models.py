from datetime import date, datetime

from beanie import PydanticObjectId

from app.shared.base_model import TenantDocument


class AttendanceRecord(TenantDocument):
    employee_id: PydanticObjectId
    date: date
    check_in: datetime | None = None
    check_out: datetime | None = None
    status: str = "present"
    notes: str = ""
    hours_worked: float = 0.0

    class Settings:
        name = "attendance_records"
        indexes = [
            [("tenant_id", 1), ("employee_id", 1), ("date", 1)],
            [("tenant_id", 1), ("date", 1)],
        ]


class LeaveType(TenantDocument):
    code: str
    name: str
    days_allowed: float = 0
    is_paid: bool = True

    class Settings:
        name = "leave_types"
        indexes = [[("tenant_id", 1), ("code", 1)]]


class LeaveRequest(TenantDocument):
    employee_id: PydanticObjectId
    leave_type_id: PydanticObjectId
    start_date: date
    end_date: date
    days: float
    reason: str = ""
    status: str = "pending"
    workflow_instance_id: PydanticObjectId | None = None
    approved_by: PydanticObjectId | None = None

    class Settings:
        name = "leave_requests"
        indexes = [
            [("tenant_id", 1), ("employee_id", 1)],
            [("tenant_id", 1), ("status", 1)],
        ]
