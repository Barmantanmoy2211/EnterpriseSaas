from fastapi import APIRouter, Depends, Query, status

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
from app.performance.service import (
    ExitService,
    OnboardingService,
    PerformanceService,
    TrainingService,
)
from app.permissions.dependencies import require_permission

router = APIRouter(tags=["performance"])


@router.get("/performance/reviews", response_model=list[ReviewResponse])
async def list_reviews(
    employee_id: str | None = Query(None),
    user=Depends(require_permission("performance", "read")),
):
    return await PerformanceService.list_reviews(str(user.tenant_id), employee_id)


@router.post("/performance/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    data: ReviewCreate,
    user=Depends(require_permission("performance", "manage")),
):
    return await PerformanceService.create_review(str(user.tenant_id), data, str(user.id))


@router.get("/performance/goals", response_model=list[GoalResponse])
async def list_goals(
    employee_id: str | None = Query(None),
    user=Depends(require_permission("performance", "read")),
):
    return await PerformanceService.list_goals(str(user.tenant_id), employee_id)


@router.post("/performance/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    data: GoalCreate,
    user=Depends(require_permission("performance", "manage")),
):
    return await PerformanceService.create_goal(str(user.tenant_id), data, str(user.id))


@router.patch("/performance/goals/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    data: GoalUpdate,
    user=Depends(require_permission("performance", "manage")),
):
    return await PerformanceService.update_goal(str(user.tenant_id), goal_id, data)


@router.get("/training/courses", response_model=list[CourseResponse])
async def list_courses(user=Depends(require_permission("training", "read"))):
    return await TrainingService.list_courses(str(user.tenant_id))


@router.post("/training/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    data: CourseCreate,
    user=Depends(require_permission("training", "manage")),
):
    return await TrainingService.create_course(str(user.tenant_id), data, str(user.id))


@router.get("/training/enrollments", response_model=list[EnrollmentResponse])
async def list_enrollments(
    employee_id: str | None = Query(None),
    user=Depends(require_permission("training", "read")),
):
    return await TrainingService.list_enrollments(str(user.tenant_id), employee_id)


@router.post("/training/enrollments", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def create_enrollment(
    data: EnrollmentCreate,
    user=Depends(require_permission("training", "manage")),
):
    return await TrainingService.enroll(str(user.tenant_id), data, str(user.id))


@router.patch("/training/enrollments/{enrollment_id}", response_model=EnrollmentResponse)
async def update_enrollment(
    enrollment_id: str,
    data: EnrollmentUpdate,
    user=Depends(require_permission("training", "manage")),
):
    return await TrainingService.update_enrollment(str(user.tenant_id), enrollment_id, data)


@router.get("/onboarding/templates", response_model=list[OnboardingTemplateResponse])
async def list_onboarding_templates(user=Depends(require_permission("onboarding", "read"))):
    return await OnboardingService.list_templates(str(user.tenant_id))


@router.post("/onboarding/templates", response_model=OnboardingTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_onboarding_template(
    data: OnboardingTemplateCreate,
    user=Depends(require_permission("onboarding", "manage")),
):
    return await OnboardingService.create_template(str(user.tenant_id), data, str(user.id))


@router.get("/onboarding/plans", response_model=list[OnboardingPlanResponse])
async def list_onboarding_plans(
    employee_id: str | None = Query(None),
    user=Depends(require_permission("onboarding", "read")),
):
    return await OnboardingService.list_plans(str(user.tenant_id), employee_id)


@router.post("/onboarding/plans", response_model=OnboardingPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_onboarding_plan(
    data: OnboardingPlanCreate,
    user=Depends(require_permission("onboarding", "manage")),
):
    return await OnboardingService.create_plan(str(user.tenant_id), data, str(user.id))


@router.patch("/onboarding/plans/{plan_id}", response_model=OnboardingPlanResponse)
async def update_onboarding_plan(
    plan_id: str,
    data: OnboardingPlanUpdate,
    user=Depends(require_permission("onboarding", "manage")),
):
    return await OnboardingService.update_plan(str(user.tenant_id), plan_id, data)


@router.get("/exit/requests", response_model=list[ExitRequestResponse])
async def list_exit_requests(
    status: str | None = Query(None),
    user=Depends(require_permission("exit", "read")),
):
    return await ExitService.list_requests(str(user.tenant_id), status)


@router.post("/exit/requests", response_model=ExitRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_exit_request(
    data: ExitRequestCreate,
    user=Depends(require_permission("exit", "manage")),
):
    return await ExitService.create_request(str(user.tenant_id), data, str(user.id))


@router.patch("/exit/requests/{request_id}/status", response_model=ExitRequestResponse)
async def update_exit_status(
    request_id: str,
    status: str = Query(...),
    user=Depends(require_permission("exit", "manage")),
):
    return await ExitService.update_status(str(user.tenant_id), request_id, status, str(user.id))
