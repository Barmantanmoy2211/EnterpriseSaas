from beanie import PydanticObjectId

from app.finance.models import Account, JournalEntry


class FinanceRepository:
    @staticmethod
    async def list_accounts(tenant_id: str, account_type: str | None = None) -> list[Account]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if account_type:
            filt["account_type"] = account_type
        return await Account.find(filt).sort("+code").to_list()

    @staticmethod
    async def get_account(tenant_id: str, account_id: str) -> Account | None:
        account = await Account.get(account_id)
        if account and str(account.tenant_id) == tenant_id and not account.is_deleted:
            return account
        return None

    @staticmethod
    async def get_account_by_code(tenant_id: str, code: str) -> Account | None:
        return await Account.find_one(
            {"tenant_id": PydanticObjectId(tenant_id), "code": code, "is_deleted": False}
        )

    @staticmethod
    async def create_account(tenant_id: str, data: dict) -> Account:
        account = Account(tenant_id=PydanticObjectId(tenant_id), **data)
        await account.insert()
        return account

    @staticmethod
    async def update_account(account: Account, data: dict) -> Account:
        for key, value in data.items():
            if value is not None:
                setattr(account, key, value)
        await account.touch()
        return account

    @staticmethod
    async def soft_delete_account(account: Account) -> None:
        await account.soft_delete()

    @staticmethod
    async def list_entries(tenant_id: str, account_id: str | None = None) -> list[JournalEntry]:
        filt: dict = {"tenant_id": PydanticObjectId(tenant_id), "is_deleted": False}
        if account_id:
            filt["account_id"] = PydanticObjectId(account_id)
        return await JournalEntry.find(filt).sort("-posted_at").to_list()

    @staticmethod
    async def create_entry(tenant_id: str, data: dict) -> JournalEntry:
        entry = JournalEntry(tenant_id=PydanticObjectId(tenant_id), **data)
        await entry.insert()
        return entry
