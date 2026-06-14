from datetime import date

from beanie import PydanticObjectId

from app.attendance.models import AttendanceRecord, LeaveRequest, LeaveType


class AttendanceRepository:
    @staticmethod
    async def list_records(
        tenant_id: str, employee_id: str | None = None, from_date: date | None = None
    ) -> list[AttendanceRecord]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if employee_id:
            filt["employee_id"] = PydanticObjectId(employee_id)
        if from_date:
            filt["date"] = {"$gte": from_date}
        return await AttendanceRecord.find(filt).sort("-date").to_list()

    @staticmethod
    async def get_record(tenant_id: str, record_id: str) -> AttendanceRecord | None:
        r = await AttendanceRecord.get(record_id)
        if r and str(r.tenant_id) == tenant_id and not r.is_deleted:
            return r
        return None

    @staticmethod
    async def get_by_employee_date(
        tenant_id: str, employee_id: str, day: date
    ) -> AttendanceRecord | None:
        return await AttendanceRecord.find_one(
            {
                "tenant_id": PydanticObjectId(tenant_id),
                "employee_id": PydanticObjectId(employee_id),
                "date": day,
                "is_deleted": False,
            }
        )

    @staticmethod
    async def create_record(tenant_id: str, data: dict) -> AttendanceRecord:
        r = AttendanceRecord(tenant_id=PydanticObjectId(tenant_id), **data)
        await r.insert()
        return r

    @staticmethod
    async def update_record(record: AttendanceRecord, data: dict) -> AttendanceRecord:
        for k, v in data.items():
            if v is not None:
                setattr(record, k, v)
        await record.touch()
        return record


class LeaveRepository:
    @staticmethod
    async def list_types(tenant_id: str) -> list[LeaveType]:
        return await LeaveType.find(
            {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        ).to_list()

    @staticmethod
    async def get_type(tenant_id: str, type_id: str) -> LeaveType | None:
        t = await LeaveType.get(type_id)
        if t and str(t.tenant_id) == tenant_id and not t.is_deleted:
            return t
        return None

    @staticmethod
    async def create_type(tenant_id: str, data: dict) -> LeaveType:
        t = LeaveType(tenant_id=PydanticObjectId(tenant_id), **data)
        await t.insert()
        return t

    @staticmethod
    async def list_requests(
        tenant_id: str, employee_id: str | None = None, status: str | None = None
    ) -> list[LeaveRequest]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if employee_id:
            filt["employee_id"] = PydanticObjectId(employee_id)
        if status:
            filt["status"] = status
        return await LeaveRequest.find(filt).sort("-created_at").to_list()

    @staticmethod
    async def get_request(tenant_id: str, request_id: str) -> LeaveRequest | None:
        r = await LeaveRequest.get(request_id)
        if r and str(r.tenant_id) == tenant_id and not r.is_deleted:
            return r
        return None

    @staticmethod
    async def create_request(tenant_id: str, data: dict) -> LeaveRequest:
        r = LeaveRequest(tenant_id=PydanticObjectId(tenant_id), **data)
        await r.insert()
        return r

    @staticmethod
    async def update_request(req: LeaveRequest, data: dict) -> LeaveRequest:
        for k, v in data.items():
            if v is not None:
                setattr(req, k, v)
        await req.touch()
        return req
