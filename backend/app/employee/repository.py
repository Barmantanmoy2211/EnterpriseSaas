from beanie import PydanticObjectId

from app.employee.models import Employee


class EmployeeRepository:
    @staticmethod
    async def list_all(tenant_id: str, status: str | None = None) -> list[Employee]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if status:
            filt["status"] = status
        return await Employee.find(filt).sort("+last_name").to_list()

    @staticmethod
    async def get(tenant_id: str, employee_id: str) -> Employee | None:
        emp = await Employee.get(employee_id)
        if emp and str(emp.tenant_id) == tenant_id and not emp.is_deleted:
            return emp
        return None

    @staticmethod
    async def get_by_code(tenant_id: str, code: str) -> Employee | None:
        return await Employee.find_one(
            {
                "tenant_id": PydanticObjectId(tenant_id),
                "employee_code": code,
                "is_deleted": False,
            }
        )

    @staticmethod
    async def create(tenant_id: str, data: dict) -> Employee:
        emp = Employee(tenant_id=PydanticObjectId(tenant_id), **data)
        await emp.insert()
        return emp

    @staticmethod
    async def update(emp: Employee, data: dict) -> Employee:
        for key, value in data.items():
            if value is not None:
                setattr(emp, key, value)
        await emp.touch()
        return emp

    @staticmethod
    async def soft_delete(emp: Employee) -> None:
        await emp.soft_delete()
