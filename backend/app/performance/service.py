from datetime import UTC, datetime

from beanie import PydanticObjectId

from app.audit.service import AuditService
from app.performance.models import (
    ExitRequest,
    OnboardingPlan,
    OnboardingTemplate,
    PerformanceGoal,
    PerformanceReview,
    TrainingCourse,
    TrainingEnrollment,
)
from app.performance.repository import (
    ExitRepository,
    OnboardingRepository,
    PerformanceRepository,
    TrainingRepository,
)
from app.performance.schemas import (
    CourseCreate,
    CourseResponse,
    EnrollmentCreate,
    EnrollmentResponse,
    EnrollmentUpdate,
    ExitRequestCreate,
    ExitRequestResponse,
    GoalCreate,
    GoalResponse,
    GoalUpdate,
    OnboardingPlanCreate,
    OnboardingPlanResponse,
    OnboardingPlanUpdate,
    OnboardingTemplateCreate,
    OnboardingTemplateResponse,
    ReviewCreate,
    ReviewResponse,
)
from app.shared.exceptions import NotFoundError


class PerformanceService:
    @staticmethod
    def _review(r: PerformanceReview) -> ReviewResponse:
        return ReviewResponse(
            id=str(r.id),
            employee_id=str(r.employee_id),
            reviewer_id=str(r.reviewer_id),
            period=r.period,
            rating=r.rating,
            feedback=r.feedback,
            goals_summary=r.goals_summary,
            status=r.status,
        )

    @staticmethod
    def _goal(g: PerformanceGoal) -> GoalResponse:
        return GoalResponse(
            id=str(g.id),
            employee_id=str(g.employee_id),
            title=g.title,
            description=g.description,
            target_date=g.target_date,
            status=g.status,
            progress=g.progress,
        )

    @staticmethod
    async def list_reviews(tenant_id: str, employee_id: str | None = None) -> list[ReviewResponse]:
        reviews = await PerformanceRepository.list_reviews(tenant_id, employee_id)
        return [PerformanceService._review(r) for r in reviews]

    @staticmethod
    async def create_review(tenant_id: str, data: ReviewCreate, reviewer_id: str) -> ReviewResponse:
        r = await PerformanceRepository.create_review(
            tenant_id,
            {
                "employee_id": PydanticObjectId(data.employee_id),
                "reviewer_id": PydanticObjectId(reviewer_id),
                "period": data.period,
                "rating": data.rating,
                "feedback": data.feedback,
                "goals_summary": data.goals_summary,
                "status": "submitted",
            },
        )
        await AuditService.log_event(tenant_id, "performance.review.created", "review", str(r.id), reviewer_id)
        return PerformanceService._review(r)

    @staticmethod
    async def list_goals(tenant_id: str, employee_id: str | None = None) -> list[GoalResponse]:
        goals = await PerformanceRepository.list_goals(tenant_id, employee_id)
        return [PerformanceService._goal(g) for g in goals]

    @staticmethod
    async def create_goal(tenant_id: str, data: GoalCreate, actor_id: str) -> GoalResponse:
        g = await PerformanceRepository.create_goal(
            tenant_id,
            {
                "employee_id": PydanticObjectId(data.employee_id),
                "title": data.title,
                "description": data.description,
                "target_date": data.target_date,
            },
        )
        return PerformanceService._goal(g)

    @staticmethod
    async def update_goal(tenant_id: str, goal_id: str, data: GoalUpdate) -> GoalResponse:
        g = await PerformanceRepository.get_goal(tenant_id, goal_id)
        if g is None:
            raise NotFoundError("Goal not found")
        updated = await PerformanceRepository.update_goal(g, data.model_dump(exclude_unset=True))
        return PerformanceService._goal(updated)


class TrainingService:
    @staticmethod
    def _course(c: TrainingCourse) -> CourseResponse:
        return CourseResponse(
            id=str(c.id),
            title=c.title,
            description=c.description,
            duration_hours=c.duration_hours,
            is_mandatory=c.is_mandatory,
            category=c.category,
        )

    @staticmethod
    def _enrollment(e: TrainingEnrollment) -> EnrollmentResponse:
        return EnrollmentResponse(
            id=str(e.id),
            course_id=str(e.course_id),
            employee_id=str(e.employee_id),
            status=e.status,
            completed_at=e.completed_at,
            score=e.score,
        )

    @staticmethod
    async def list_courses(tenant_id: str) -> list[CourseResponse]:
        courses = await TrainingRepository.list_courses(tenant_id)
        return [TrainingService._course(c) for c in courses]

    @staticmethod
    async def create_course(tenant_id: str, data: CourseCreate, actor_id: str) -> CourseResponse:
        c = await TrainingRepository.create_course(tenant_id, data.model_dump())
        return TrainingService._course(c)

    @staticmethod
    async def list_enrollments(
        tenant_id: str, employee_id: str | None = None
    ) -> list[EnrollmentResponse]:
        enrollments = await TrainingRepository.list_enrollments(tenant_id, employee_id)
        return [TrainingService._enrollment(e) for e in enrollments]

    @staticmethod
    async def enroll(tenant_id: str, data: EnrollmentCreate, actor_id: str) -> EnrollmentResponse:
        e = await TrainingRepository.create_enrollment(
            tenant_id,
            {
                "course_id": PydanticObjectId(data.course_id),
                "employee_id": PydanticObjectId(data.employee_id),
            },
        )
        return TrainingService._enrollment(e)

    @staticmethod
    async def update_enrollment(
        tenant_id: str, enrollment_id: str, data: EnrollmentUpdate
    ) -> EnrollmentResponse:
        e = await TrainingRepository.get_enrollment(tenant_id, enrollment_id)
        if e is None:
            raise NotFoundError("Enrollment not found")
        update = data.model_dump(exclude_unset=True)
        if update.get("status") == "completed":
            update["completed_at"] = datetime.now(UTC)
        updated = await TrainingRepository.update_enrollment(e, update)
        return TrainingService._enrollment(updated)


class OnboardingService:
    @staticmethod
    def _template(t: OnboardingTemplate) -> OnboardingTemplateResponse:
        return OnboardingTemplateResponse(
            id=str(t.id), name=t.name, description=t.description, tasks=t.tasks
        )

    @staticmethod
    def _plan(p: OnboardingPlan) -> OnboardingPlanResponse:
        return OnboardingPlanResponse(
            id=str(p.id),
            employee_id=str(p.employee_id),
            template_id=str(p.template_id) if p.template_id else None,
            status=p.status,
            tasks=p.tasks,
        )

    @staticmethod
    async def list_templates(tenant_id: str) -> list[OnboardingTemplateResponse]:
        templates = await OnboardingRepository.list_templates(tenant_id)
        return [OnboardingService._template(t) for t in templates]

    @staticmethod
    async def create_template(
        tenant_id: str, data: OnboardingTemplateCreate, actor_id: str
    ) -> OnboardingTemplateResponse:
        t = await OnboardingRepository.create_template(tenant_id, data.model_dump())
        return OnboardingService._template(t)

    @staticmethod
    async def list_plans(
        tenant_id: str, employee_id: str | None = None
    ) -> list[OnboardingPlanResponse]:
        plans = await OnboardingRepository.list_plans(tenant_id, employee_id)
        return [OnboardingService._plan(p) for p in plans]

    @staticmethod
    async def create_plan(
        tenant_id: str, data: OnboardingPlanCreate, actor_id: str
    ) -> OnboardingPlanResponse:
        payload: dict = {"employee_id": PydanticObjectId(data.employee_id), "tasks": data.tasks}
        if data.template_id:
            payload["template_id"] = PydanticObjectId(data.template_id)
        p = await OnboardingRepository.create_plan(tenant_id, payload)
        await AuditService.log_event(tenant_id, "onboarding.plan.created", "onboarding", str(p.id), actor_id)
        return OnboardingService._plan(p)

    @staticmethod
    async def update_plan(
        tenant_id: str, plan_id: str, data: OnboardingPlanUpdate
    ) -> OnboardingPlanResponse:
        p = await OnboardingRepository.get_plan(tenant_id, plan_id)
        if p is None:
            raise NotFoundError("Onboarding plan not found")
        updated = await OnboardingRepository.update_plan(p, data.model_dump(exclude_unset=True))
        return OnboardingService._plan(updated)


class ExitService:
    @staticmethod
    def _request(r: ExitRequest) -> ExitRequestResponse:
        return ExitRequestResponse(
            id=str(r.id),
            employee_id=str(r.employee_id),
            exit_type=r.exit_type,
            last_working_date=r.last_working_date,
            reason=r.reason,
            status=r.status,
            workflow_instance_id=str(r.workflow_instance_id) if r.workflow_instance_id else None,
        )

    @staticmethod
    async def list_requests(tenant_id: str, status: str | None = None) -> list[ExitRequestResponse]:
        requests = await ExitRepository.list_requests(tenant_id, status)
        return [ExitService._request(r) for r in requests]

    @staticmethod
    async def create_request(
        tenant_id: str, data: ExitRequestCreate, actor_id: str
    ) -> ExitRequestResponse:
        r = await ExitRepository.create_request(
            tenant_id,
            {
                "employee_id": PydanticObjectId(data.employee_id),
                "exit_type": data.exit_type,
                "last_working_date": data.last_working_date,
                "reason": data.reason,
            },
        )
        await AuditService.log_event(tenant_id, "exit.requested", "exit_request", str(r.id), actor_id)
        return ExitService._request(r)

    @staticmethod
    async def update_status(
        tenant_id: str, request_id: str, status: str, actor_id: str
    ) -> ExitRequestResponse:
        r = await ExitRepository.get_request(tenant_id, request_id)
        if r is None:
            raise NotFoundError("Exit request not found")
        updated = await ExitRepository.update_request(r, {"status": status})
        if status == "approved":
            from app.employee.repository import EmployeeRepository

            emp = await EmployeeRepository.get(tenant_id, str(r.employee_id))
            if emp:
                await EmployeeRepository.update(emp, {"status": "terminated"})
        return ExitService._request(updated)
