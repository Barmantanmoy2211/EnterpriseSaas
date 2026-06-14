from datetime import date, datetime

from pydantic import BaseModel, Field


class AttendanceCreate(BaseModel):
    employee_id: str
    date: date
    status: str = "present"
    notes: str = ""


class AttendanceCheckIn(BaseModel):
    employee_id: str


class AttendanceCheckOut(BaseModel):
    employee_id: str


class AttendanceResponse(BaseModel):
    id: str
    employee_id: str
    date: date
    check_in: datetime | None
    check_out: datetime | None
    status: str
    notes: str
    hours_worked: float


class LeaveTypeCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str
    days_allowed: float = 0
    is_paid: bool = True


class LeaveTypeResponse(BaseModel):
    id: str
    code: str
    name: str
    days_allowed: float
    is_paid: bool


class LeaveRequestCreate(BaseModel):
    employee_id: str
    leave_type_id: str
    start_date: date
    end_date: date
    days: float
    reason: str = ""
    start_workflow: bool = True
    scope_node_id: str | None = None


class LeaveRequestResponse(BaseModel):
    id: str
    employee_id: str
    leave_type_id: str
    start_date: date
    end_date: date
    days: float
    reason: str
    status: str
    workflow_instance_id: str | None
