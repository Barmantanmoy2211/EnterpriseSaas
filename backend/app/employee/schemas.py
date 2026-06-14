from datetime import date
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class EmployeeCreate(BaseModel):
    employee_code: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = ""
    user_id: str | None = None
    org_node_id: str | None = None
    job_title: str = ""
    department: str = ""
    employment_type: str = "full_time"
    hire_date: date | None = None
    manager_id: str | None = None
    profile: dict[str, Any] = Field(default_factory=dict)


class EmployeeUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    org_node_id: str | None = None
    job_title: str | None = None
    department: str | None = None
    employment_type: str | None = None
    status: str | None = None
    hire_date: date | None = None
    manager_id: str | None = None
    profile: dict[str, Any] | None = None


class EmployeeResponse(BaseModel):
    id: str
    user_id: str | None
    employee_code: str
    first_name: str
    last_name: str
    email: str
    phone: str
    org_node_id: str | None
    job_title: str
    department: str
    employment_type: str
    status: str
    hire_date: date | None
    manager_id: str | None
    profile: dict[str, Any]
