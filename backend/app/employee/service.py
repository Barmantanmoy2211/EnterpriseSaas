from beanie import PydanticObjectId

from app.audit.service import AuditService
from app.employee.models import Employee
from app.employee.repository import EmployeeRepository
from app.employee.schemas import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.search.repository import SearchRepository
from app.shared.exceptions import ConflictError, NotFoundError


class EmployeeService:
    @staticmethod
    def _response(emp: Employee) -> EmployeeResponse:
        return EmployeeResponse(
            id=str(emp.id),
            user_id=str(emp.user_id) if emp.user_id else None,
            employee_code=emp.employee_code,
            first_name=emp.first_name,
            last_name=emp.last_name,
            email=emp.email,
            phone=emp.phone,
            org_node_id=str(emp.org_node_id) if emp.org_node_id else None,
            job_title=emp.job_title,
            department=emp.department,
            employment_type=emp.employment_type,
            status=emp.status,
            hire_date=emp.hire_date,
            manager_id=str(emp.manager_id) if emp.manager_id else None,
            profile=emp.profile,
        )

    @staticmethod
    async def _index(emp: Employee) -> None:
        name = f"{emp.first_name} {emp.last_name}"
        await SearchRepository.upsert(
            str(emp.tenant_id),
            "employee",
            str(emp.id),
            name,
            f"{emp.job_title} {emp.department} {emp.email}",
            [emp.employee_code, emp.email, emp.first_name, emp.last_name],
            {"status": emp.status},
        )

    @staticmethod
    async def list_employees(
        tenant_id: str,
        status: str | None = None,
        user_id: str | None = None,
    ) -> list[EmployeeResponse]:
        employees = await EmployeeRepository.list_all(tenant_id, status)
        if user_id:
            from app.shared.org_scope import get_visible_org_node_ids, record_in_org_scope

            visible = await get_visible_org_node_ids(tenant_id, user_id)
            if visible is not None:
                employees = [
                    e
                    for e in employees
                    if record_in_org_scope(
                        str(e.org_node_id) if e.org_node_id else None,
                        visible,
                    )
                ]
        return [EmployeeService._response(e) for e in employees]

    @staticmethod
    async def get_employee(tenant_id: str, employee_id: str) -> EmployeeResponse:
        emp = await EmployeeRepository.get(tenant_id, employee_id)
        if emp is None:
            raise NotFoundError("Employee not found")
        return EmployeeService._response(emp)

    @staticmethod
    async def create_employee(tenant_id: str, data: EmployeeCreate, actor_id: str) -> EmployeeResponse:
        existing = await EmployeeRepository.get_by_code(tenant_id, data.employee_code)
        if existing:
            raise ConflictError(f"Employee code '{data.employee_code}' already exists")

        payload = data.model_dump(exclude={"user_id", "org_node_id", "manager_id"})
        if data.user_id:
            payload["user_id"] = PydanticObjectId(data.user_id)
        if data.org_node_id:
            payload["org_node_id"] = PydanticObjectId(data.org_node_id)
        if data.manager_id:
            payload["manager_id"] = PydanticObjectId(data.manager_id)

        emp = await EmployeeRepository.create(tenant_id, payload)
        await EmployeeService._index(emp)
        await AuditService.log_event(
            tenant_id, "employee.created", "employee", str(emp.id), actor_id
        )
        return EmployeeService._response(emp)

    @staticmethod
    async def update_employee(
        tenant_id: str, employee_id: str, data: EmployeeUpdate, actor_id: str
    ) -> EmployeeResponse:
        emp = await EmployeeRepository.get(tenant_id, employee_id)
        if emp is None:
            raise NotFoundError("Employee not found")

        update_data = data.model_dump(exclude_unset=True)
        for field in ("org_node_id", "manager_id"):
            if field in update_data and update_data[field] is not None:
                update_data[field] = PydanticObjectId(update_data[field])

        updated = await EmployeeRepository.update(emp, update_data)
        await EmployeeService._index(updated)
        await AuditService.log_event(
            tenant_id, "employee.updated", "employee", employee_id, actor_id
        )
        return EmployeeService._response(updated)

    @staticmethod
    async def delete_employee(tenant_id: str, employee_id: str, actor_id: str) -> None:
        emp = await EmployeeRepository.get(tenant_id, employee_id)
        if emp is None:
            raise NotFoundError("Employee not found")
        await EmployeeRepository.soft_delete(emp)
        await SearchRepository.remove(tenant_id, "employee", employee_id)
        await AuditService.log_event(
            tenant_id, "employee.deleted", "employee", employee_id, actor_id
        )
