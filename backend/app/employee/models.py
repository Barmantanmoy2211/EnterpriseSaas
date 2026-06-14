from datetime import date
from typing import Any

from beanie import PydanticObjectId
from pydantic import EmailStr, Field

from app.shared.base_model import TenantDocument


class Employee(TenantDocument):
    user_id: PydanticObjectId | None = None
    employee_code: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: str = ""
    org_node_id: PydanticObjectId | None = None
    job_title: str = ""
    department: str = ""
    employment_type: str = "full_time"
    status: str = "active"
    hire_date: date | None = None
    manager_id: PydanticObjectId | None = None
    profile: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "employees"
        indexes = [
            [("tenant_id", 1), ("employee_code", 1)],
            [("tenant_id", 1), ("email", 1)],
            [("tenant_id", 1), ("status", 1)],
            [("tenant_id", 1), ("org_node_id", 1)],
        ]
