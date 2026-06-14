from datetime import date, datetime

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    employee_id: str
    period: str
    rating: int | None = Field(None, ge=1, le=5)
    feedback: str = ""
    goals_summary: str = ""


class ReviewResponse(BaseModel):
    id: str
    employee_id: str
    reviewer_id: str
    period: str
    rating: int | None
    feedback: str
    goals_summary: str
    status: str


class GoalCreate(BaseModel):
    employee_id: str
    title: str
    description: str = ""
    target_date: date | None = None


class GoalUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    progress: int | None = Field(None, ge=0, le=100)


class GoalResponse(BaseModel):
    id: str
    employee_id: str
    title: str
    description: str
    target_date: date | None
    status: str
    progress: int


class CourseCreate(BaseModel):
    title: str
    description: str = ""
    duration_hours: float = 0
    is_mandatory: bool = False
    category: str = ""


class CourseResponse(BaseModel):
    id: str
    title: str
    description: str
    duration_hours: float
    is_mandatory: bool
    category: str


class EnrollmentCreate(BaseModel):
    course_id: str
    employee_id: str


class EnrollmentUpdate(BaseModel):
    status: str | None = None
    score: float | None = None


class EnrollmentResponse(BaseModel):
    id: str
    course_id: str
    employee_id: str
    status: str
    completed_at: datetime | None
    score: float | None


class OnboardingTemplateCreate(BaseModel):
    name: str
    description: str = ""
    tasks: list[dict] = Field(default_factory=list)


class OnboardingTemplateResponse(BaseModel):
    id: str
    name: str
    description: str
    tasks: list[dict]


class OnboardingPlanCreate(BaseModel):
    employee_id: str
    template_id: str | None = None
    tasks: list[dict] = Field(default_factory=list)


class OnboardingPlanUpdate(BaseModel):
    status: str | None = None
    tasks: list[dict] | None = None


class OnboardingPlanResponse(BaseModel):
    id: str
    employee_id: str
    template_id: str | None
    status: str
    tasks: list[dict]


class ExitRequestCreate(BaseModel):
    employee_id: str
    exit_type: str = "resignation"
    last_working_date: date
    reason: str = ""


class ExitRequestResponse(BaseModel):
    id: str
    employee_id: str
    exit_type: str
    last_working_date: date
    reason: str
    status: str
    workflow_instance_id: str | None
