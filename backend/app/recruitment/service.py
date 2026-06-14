from beanie import PydanticObjectId

from app.audit.service import AuditService
from app.recruitment.models import Candidate, JobApplication, JobPosting
from app.recruitment.repository import RecruitmentRepository
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
from app.search.repository import SearchRepository
from app.shared.exceptions import NotFoundError


class RecruitmentService:
    @staticmethod
    def _job(j: JobPosting) -> JobResponse:
        return JobResponse(
            id=str(j.id),
            title=j.title,
            description=j.description,
            org_node_id=str(j.org_node_id) if j.org_node_id else None,
            status=j.status,
            requirements=j.requirements,
            location=j.location,
            employment_type=j.employment_type,
        )

    @staticmethod
    def _candidate(c: Candidate) -> CandidateResponse:
        return CandidateResponse(
            id=str(c.id),
            first_name=c.first_name,
            last_name=c.last_name,
            email=c.email,
            phone=c.phone,
            resume_url=c.resume_url,
            source=c.source,
        )

    @staticmethod
    def _application(a: JobApplication) -> ApplicationResponse:
        return ApplicationResponse(
            id=str(a.id),
            job_id=str(a.job_id),
            candidate_id=str(a.candidate_id),
            status=a.status,
            notes=a.notes,
            stage_history=a.stage_history,
        )

    @staticmethod
    async def list_jobs(tenant_id: str, status: str | None = None) -> list[JobResponse]:
        jobs = await RecruitmentRepository.list_jobs(tenant_id, status)
        return [RecruitmentService._job(j) for j in jobs]

    @staticmethod
    async def create_job(tenant_id: str, data: JobCreate, actor_id: str) -> JobResponse:
        payload = data.model_dump()
        if data.org_node_id:
            payload["org_node_id"] = PydanticObjectId(data.org_node_id)
        job = await RecruitmentRepository.create_job(tenant_id, payload)
        await SearchRepository.upsert(
            tenant_id, "job", str(job.id), job.title, job.description, [job.title, job.location]
        )
        await AuditService.log_event(tenant_id, "recruitment.job.created", "job", str(job.id), actor_id)
        return RecruitmentService._job(job)

    @staticmethod
    async def update_job(tenant_id: str, job_id: str, data: JobUpdate, actor_id: str) -> JobResponse:
        job = await RecruitmentRepository.get_job(tenant_id, job_id)
        if job is None:
            raise NotFoundError("Job not found")
        updated = await RecruitmentRepository.update_job(job, data.model_dump(exclude_unset=True))
        return RecruitmentService._job(updated)

    @staticmethod
    async def list_candidates(tenant_id: str) -> list[CandidateResponse]:
        candidates = await RecruitmentRepository.list_candidates(tenant_id)
        return [RecruitmentService._candidate(c) for c in candidates]

    @staticmethod
    async def create_candidate(tenant_id: str, data: CandidateCreate, actor_id: str) -> CandidateResponse:
        c = await RecruitmentRepository.create_candidate(tenant_id, data.model_dump())
        name = f"{c.first_name} {c.last_name}"
        await SearchRepository.upsert(tenant_id, "candidate", str(c.id), name, c.email, [c.email, name])
        await AuditService.log_event(tenant_id, "recruitment.candidate.created", "candidate", str(c.id), actor_id)
        return RecruitmentService._candidate(c)

    @staticmethod
    async def list_applications(
        tenant_id: str, job_id: str | None = None, status: str | None = None
    ) -> list[ApplicationResponse]:
        apps = await RecruitmentRepository.list_applications(tenant_id, job_id, status)
        return [RecruitmentService._application(a) for a in apps]

    @staticmethod
    async def create_application(
        tenant_id: str, data: ApplicationCreate, actor_id: str
    ) -> ApplicationResponse:
        job = await RecruitmentRepository.get_job(tenant_id, data.job_id)
        if job is None:
            raise NotFoundError("Job not found")
        candidate = await RecruitmentRepository.get_candidate(tenant_id, data.candidate_id)
        if candidate is None:
            raise NotFoundError("Candidate not found")
        app = await RecruitmentRepository.create_application(
            tenant_id,
            {
                "job_id": PydanticObjectId(data.job_id),
                "candidate_id": PydanticObjectId(data.candidate_id),
                "notes": data.notes,
            },
        )
        await AuditService.log_event(
            tenant_id, "recruitment.application.created", "application", str(app.id), actor_id
        )
        return RecruitmentService._application(app)

    @staticmethod
    async def update_application(
        tenant_id: str, app_id: str, data: ApplicationUpdate, actor_id: str
    ) -> ApplicationResponse:
        app = await RecruitmentRepository.get_application(tenant_id, app_id)
        if app is None:
            raise NotFoundError("Application not found")
        updated = await RecruitmentRepository.update_application(app, data.model_dump(exclude_unset=True))
        await AuditService.log_event(
            tenant_id, "recruitment.application.updated", "application", app_id, actor_id,
            {"status": updated.status},
        )
        return RecruitmentService._application(updated)
