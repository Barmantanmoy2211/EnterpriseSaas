from datetime import date

from fastapi import APIRouter, Depends, Query, status

from app.attendance.schemas import (
    AttendanceCheckIn,
    AttendanceCheckOut,
    AttendanceCreate,
    AttendanceResponse,
    LeaveRequestCreate,
    LeaveRequestResponse,
    LeaveTypeCreate,
    LeaveTypeResponse,
)
from app.attendance.service import AttendanceService, LeaveService
from app.core.security import get_current_user
from app.permissions.dependencies import require_permission

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.get("/records", response_model=list[AttendanceResponse])
async def list_attendance(
    employee_id: str | None = Query(None),
    from_date: date | None = Query(None),
    user=Depends(require_permission("attendance", "read")),
):
    return await AttendanceService.list_records(str(user.tenant_id), employee_id, from_date)


@router.post("/records", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def create_attendance(
    data: AttendanceCreate,
    user=Depends(require_permission("attendance", "manage")),
):
    return await AttendanceService.create_record(str(user.tenant_id), data, str(user.id))


@router.post("/check-in", response_model=AttendanceResponse)
async def check_in(data: AttendanceCheckIn, user=Depends(get_current_user)):
    return await AttendanceService.check_in(str(user.tenant_id), data.employee_id, str(user.id))


@router.post("/check-out", response_model=AttendanceResponse)
async def check_out(data: AttendanceCheckOut, user=Depends(get_current_user)):
    return await AttendanceService.check_out(str(user.tenant_id), data.employee_id, str(user.id))


leave_router = APIRouter(prefix="/leave", tags=["leave"])


@leave_router.get("/types", response_model=list[LeaveTypeResponse])
async def list_leave_types(user=Depends(require_permission("leave", "read"))):
    return await LeaveService.list_types(str(user.tenant_id))


@leave_router.post("/types", response_model=LeaveTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_type(
    data: LeaveTypeCreate,
    user=Depends(require_permission("leave", "manage")),
):
    return await LeaveService.create_type(str(user.tenant_id), data, str(user.id))


@leave_router.get("/requests", response_model=list[LeaveRequestResponse])
async def list_leave_requests(
    employee_id: str | None = Query(None),
    status: str | None = Query(None),
    user=Depends(require_permission("leave", "read")),
):
    return await LeaveService.list_requests(str(user.tenant_id), employee_id, status)


@leave_router.post("/requests", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_request(
    data: LeaveRequestCreate,
    user=Depends(require_permission("leave", "request")),
):
    return await LeaveService.create_request(str(user.tenant_id), data, str(user.id))
