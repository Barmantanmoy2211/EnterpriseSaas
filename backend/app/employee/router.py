from fastapi import APIRouter, Depends, Query, status

from app.employee.schemas import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.employee.service import EmployeeService
from app.permissions.dependencies import require_permission

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeResponse])
async def list_employees(
    status: str | None = Query(None),
    user=Depends(require_permission("employee", "read")),
):
    return await EmployeeService.list_employees(str(user.tenant_id), status)


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: str, user=Depends(require_permission("employee", "read"))):
    return await EmployeeService.get_employee(str(user.tenant_id), employee_id)


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    data: EmployeeCreate,
    user=Depends(require_permission("employee", "manage")),
):
    return await EmployeeService.create_employee(str(user.tenant_id), data, str(user.id))


@router.patch("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: str,
    data: EmployeeUpdate,
    user=Depends(require_permission("employee", "manage")),
):
    return await EmployeeService.update_employee(
        str(user.tenant_id), employee_id, data, str(user.id)
    )


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: str,
    user=Depends(require_permission("employee", "manage")),
):
    await EmployeeService.delete_employee(str(user.tenant_id), employee_id, str(user.id))
