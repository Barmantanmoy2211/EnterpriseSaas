from fastapi import APIRouter, Depends, Query, status

from app.permissions.dependencies import require_permission
from app.recruitment.schemas import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
    CandidateCreate,
    CandidateResponse,
    JobCreate,
    JobResponse,
    JobUpdate,
)
from app.recruitment.service import RecruitmentService

router = APIRouter(prefix="/recruitment", tags=["recruitment"])


@router.get("/jobs", response_model=list[JobResponse])
async def list_jobs(
    status: str | None = Query(None),
    user=Depends(require_permission("recruitment", "read")),
):
    return await RecruitmentService.list_jobs(str(user.tenant_id), status)


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    data: JobCreate,
    user=Depends(require_permission("recruitment", "manage")),
):
    return await RecruitmentService.create_job(str(user.tenant_id), data, str(user.id))


@router.patch("/jobs/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    data: JobUpdate,
    user=Depends(require_permission("recruitment", "manage")),
):
    return await RecruitmentService.update_job(str(user.tenant_id), job_id, data, str(user.id))


@router.get("/candidates", response_model=list[CandidateResponse])
async def list_candidates(user=Depends(require_permission("recruitment", "read"))):
    return await RecruitmentService.list_candidates(str(user.tenant_id))


@router.post("/candidates", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    data: CandidateCreate,
    user=Depends(require_permission("recruitment", "manage")),
):
    return await RecruitmentService.create_candidate(str(user.tenant_id), data, str(user.id))


@router.get("/applications", response_model=list[ApplicationResponse])
async def list_applications(
    job_id: str | None = Query(None),
    status: str | None = Query(None),
    user=Depends(require_permission("recruitment", "read")),
):
    return await RecruitmentService.list_applications(str(user.tenant_id), job_id, status)


@router.post("/applications", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    data: ApplicationCreate,
    user=Depends(require_permission("recruitment", "manage")),
):
    return await RecruitmentService.create_application(str(user.tenant_id), data, str(user.id))


@router.patch("/applications/{app_id}", response_model=ApplicationResponse)
async def update_application(
    app_id: str,
    data: ApplicationUpdate,
    user=Depends(require_permission("recruitment", "manage")),
):
    return await RecruitmentService.update_application(str(user.tenant_id), app_id, data, str(user.id))
