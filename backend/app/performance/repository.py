
from beanie import PydanticObjectId

from app.performance.models import (
    ExitRequest,
    OnboardingPlan,
    OnboardingTemplate,
    PerformanceGoal,
    PerformanceReview,
    TrainingCourse,
    TrainingEnrollment,
)


class PerformanceRepository:
    @staticmethod
    async def list_reviews(tenant_id: str, employee_id: str | None = None) -> list[PerformanceReview]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if employee_id:
            filt["employee_id"] = PydanticObjectId(employee_id)
        return await PerformanceReview.find(filt).sort("-created_at").to_list()

    @staticmethod
    async def create_review(tenant_id: str, data: dict) -> PerformanceReview:
        r = PerformanceReview(tenant_id=PydanticObjectId(tenant_id), **data)
        await r.insert()
        return r

    @staticmethod
    async def list_goals(tenant_id: str, employee_id: str | None = None) -> list[PerformanceGoal]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if employee_id:
            filt["employee_id"] = PydanticObjectId(employee_id)
        return await PerformanceGoal.find(filt).to_list()

    @staticmethod
    async def create_goal(tenant_id: str, data: dict) -> PerformanceGoal:
        g = PerformanceGoal(tenant_id=PydanticObjectId(tenant_id), **data)
        await g.insert()
        return g

    @staticmethod
    async def get_goal(tenant_id: str, goal_id: str) -> PerformanceGoal | None:
        g = await PerformanceGoal.get(goal_id)
        if g and str(g.tenant_id) == tenant_id and not g.is_deleted:
            return g
        return None

    @staticmethod
    async def update_goal(goal: PerformanceGoal, data: dict) -> PerformanceGoal:
        for k, v in data.items():
            if v is not None:
                setattr(goal, k, v)
        await goal.touch()
        return goal


class TrainingRepository:
    @staticmethod
    async def list_courses(tenant_id: str) -> list[TrainingCourse]:
        return await TrainingCourse.find(
            {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        ).to_list()

    @staticmethod
    async def create_course(tenant_id: str, data: dict) -> TrainingCourse:
        c = TrainingCourse(tenant_id=PydanticObjectId(tenant_id), **data)
        await c.insert()
        return c

    @staticmethod
    async def list_enrollments(
        tenant_id: str, employee_id: str | None = None
    ) -> list[TrainingEnrollment]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if employee_id:
            filt["employee_id"] = PydanticObjectId(employee_id)
        return await TrainingEnrollment.find(filt).to_list()

    @staticmethod
    async def create_enrollment(tenant_id: str, data: dict) -> TrainingEnrollment:
        e = TrainingEnrollment(tenant_id=PydanticObjectId(tenant_id), **data)
        await e.insert()
        return e

    @staticmethod
    async def get_enrollment(tenant_id: str, enrollment_id: str) -> TrainingEnrollment | None:
        e = await TrainingEnrollment.get(enrollment_id)
        if e and str(e.tenant_id) == tenant_id and not e.is_deleted:
            return e
        return None

    @staticmethod
    async def update_enrollment(enrollment: TrainingEnrollment, data: dict) -> TrainingEnrollment:
        for k, v in data.items():
            if v is not None:
                setattr(enrollment, k, v)
        await enrollment.touch()
        return enrollment


class OnboardingRepository:
    @staticmethod
    async def list_templates(tenant_id: str) -> list[OnboardingTemplate]:
        return await OnboardingTemplate.find(
            {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        ).to_list()

    @staticmethod
    async def create_template(tenant_id: str, data: dict) -> OnboardingTemplate:
        t = OnboardingTemplate(tenant_id=PydanticObjectId(tenant_id), **data)
        await t.insert()
        return t

    @staticmethod
    async def list_plans(tenant_id: str, employee_id: str | None = None) -> list[OnboardingPlan]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if employee_id:
            filt["employee_id"] = PydanticObjectId(employee_id)
        return await OnboardingPlan.find(filt).to_list()

    @staticmethod
    async def create_plan(tenant_id: str, data: dict) -> OnboardingPlan:
        p = OnboardingPlan(tenant_id=PydanticObjectId(tenant_id), **data)
        await p.insert()
        return p

    @staticmethod
    async def get_plan(tenant_id: str, plan_id: str) -> OnboardingPlan | None:
        p = await OnboardingPlan.get(plan_id)
        if p and str(p.tenant_id) == tenant_id and not p.is_deleted:
            return p
        return None

    @staticmethod
    async def update_plan(plan: OnboardingPlan, data: dict) -> OnboardingPlan:
        for k, v in data.items():
            if v is not None:
                setattr(plan, k, v)
        await plan.touch()
        return plan


class ExitRepository:
    @staticmethod
    async def list_requests(tenant_id: str, status: str | None = None) -> list[ExitRequest]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if status:
            filt["status"] = status
        return await ExitRequest.find(filt).sort("-created_at").to_list()

    @staticmethod
    async def create_request(tenant_id: str, data: dict) -> ExitRequest:
        r = ExitRequest(tenant_id=PydanticObjectId(tenant_id), **data)
        await r.insert()
        return r

    @staticmethod
    async def get_request(tenant_id: str, request_id: str) -> ExitRequest | None:
        r = await ExitRequest.get(request_id)
        if r and str(r.tenant_id) == tenant_id and not r.is_deleted:
            return r
        return None

    @staticmethod
    async def update_request(req: ExitRequest, data: dict) -> ExitRequest:
        for k, v in data.items():
            if v is not None:
                setattr(req, k, v)
        await req.touch()
        return req
