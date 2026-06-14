from datetime import date, datetime

from beanie import PydanticObjectId
from pydantic import Field

from app.shared.base_model import TenantDocument


class PerformanceReview(TenantDocument):
    employee_id: PydanticObjectId
    reviewer_id: PydanticObjectId
    period: str
    rating: int | None = None
    feedback: str = ""
    goals_summary: str = ""
    status: str = "draft"

    class Settings:
        name = "performance_reviews"
        indexes = [[("tenant_id", 1), ("employee_id", 1)]]


class PerformanceGoal(TenantDocument):
    employee_id: PydanticObjectId
    title: str
    description: str = ""
    target_date: date | None = None
    status: str = "in_progress"
    progress: int = 0

    class Settings:
        name = "performance_goals"
        indexes = [[("tenant_id", 1), ("employee_id", 1)]]


class TrainingCourse(TenantDocument):
    title: str
    description: str = ""
    duration_hours: float = 0
    is_mandatory: bool = False
    category: str = ""

    class Settings:
        name = "training_courses"
        indexes = [[("tenant_id", 1)]]


class TrainingEnrollment(TenantDocument):
    course_id: PydanticObjectId
    employee_id: PydanticObjectId
    status: str = "enrolled"
    completed_at: datetime | None = None
    score: float | None = None

    class Settings:
        name = "training_enrollments"
        indexes = [
            [("tenant_id", 1), ("employee_id", 1)],
            [("tenant_id", 1), ("course_id", 1)],
        ]


class OnboardingTemplate(TenantDocument):
    name: str
    description: str = ""
    tasks: list[dict] = Field(default_factory=list)

    class Settings:
        name = "onboarding_templates"
        indexes = [[("tenant_id", 1)]]


class OnboardingPlan(TenantDocument):
    employee_id: PydanticObjectId
    template_id: PydanticObjectId | None = None
    status: str = "in_progress"
    tasks: list[dict] = Field(default_factory=list)

    class Settings:
        name = "onboarding_plans"
        indexes = [[("tenant_id", 1), ("employee_id", 1)]]


class ExitRequest(TenantDocument):
    employee_id: PydanticObjectId
    exit_type: str = "resignation"
    last_working_date: date
    reason: str = ""
    status: str = "pending"
    workflow_instance_id: PydanticObjectId | None = None

    class Settings:
        name = "exit_requests"
        indexes = [[("tenant_id", 1), ("employee_id", 1)], [("tenant_id", 1), ("status", 1)]]
