from datetime import UTC, datetime

from beanie import PydanticObjectId

from app.recruitment.models import Candidate, JobApplication, JobPosting


class RecruitmentRepository:
    # Jobs
    @staticmethod
    async def list_jobs(tenant_id: str, status: str | None = None) -> list[JobPosting]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if status:
            filt["status"] = status
        return await JobPosting.find(filt).sort("-created_at").to_list()

    @staticmethod
    async def get_job(tenant_id: str, job_id: str) -> JobPosting | None:
        j = await JobPosting.get(job_id)
        if j and str(j.tenant_id) == tenant_id and not j.is_deleted:
            return j
        return None

    @staticmethod
    async def create_job(tenant_id: str, data: dict) -> JobPosting:
        job = JobPosting(tenant_id=PydanticObjectId(tenant_id), **data)
        await job.insert()
        return job

    @staticmethod
    async def update_job(job: JobPosting, data: dict) -> JobPosting:
        for k, v in data.items():
            if v is not None:
                setattr(job, k, v)
        await job.touch()
        return job

    # Candidates
    @staticmethod
    async def list_candidates(tenant_id: str) -> list[Candidate]:
        return await Candidate.find(
            {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        ).sort("+last_name").to_list()

    @staticmethod
    async def get_candidate(tenant_id: str, candidate_id: str) -> Candidate | None:
        c = await Candidate.get(candidate_id)
        if c and str(c.tenant_id) == tenant_id and not c.is_deleted:
            return c
        return None

    @staticmethod
    async def create_candidate(tenant_id: str, data: dict) -> Candidate:
        c = Candidate(tenant_id=PydanticObjectId(tenant_id), **data)
        await c.insert()
        return c

    # Applications
    @staticmethod
    async def list_applications(
        tenant_id: str, job_id: str | None = None, status: str | None = None
    ) -> list[JobApplication]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if job_id:
            filt["job_id"] = PydanticObjectId(job_id)
        if status:
            filt["status"] = status
        return await JobApplication.find(filt).sort("-created_at").to_list()

    @staticmethod
    async def get_application(tenant_id: str, app_id: str) -> JobApplication | None:
        a = await JobApplication.get(app_id)
        if a and str(a.tenant_id) == tenant_id and not a.is_deleted:
            return a
        return None

    @staticmethod
    async def create_application(tenant_id: str, data: dict) -> JobApplication:
        data["stage_history"] = [
            {"status": data.get("status", "applied"), "at": datetime.now(UTC).isoformat()}
        ]
        a = JobApplication(tenant_id=PydanticObjectId(tenant_id), **data)
        await a.insert()
        return a

    @staticmethod
    async def update_application(app: JobApplication, data: dict) -> JobApplication:
        if "status" in data and data["status"] and data["status"] != app.status:
            app.stage_history.append(
                {"status": data["status"], "at": datetime.now(UTC).isoformat()}
            )
        for k, v in data.items():
            if v is not None and k != "stage_history":
                setattr(app, k, v)
        await app.touch()
        return app
