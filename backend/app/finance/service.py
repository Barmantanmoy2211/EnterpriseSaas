from beanie import PydanticObjectId

from app.audit.service import AuditService
from app.finance.models import Account
from app.finance.repository import FinanceRepository
from app.finance.schemas import (
    AccountCreate,
    AccountResponse,
    AccountUpdate,
    JournalEntryCreate,
    JournalEntryResponse,
)
from app.shared.exceptions import ConflictError, NotFoundError, ValidationError


class FinanceService:
    @staticmethod
    def _account_response(account: Account) -> AccountResponse:
        return AccountResponse(
            id=str(account.id),
            code=account.code,
            name=account.name,
            account_type=account.account_type,
            balance=account.balance,
            currency=account.currency,
            is_active=account.is_active,
            metadata=account.metadata,
        )

    @staticmethod
    async def list_accounts(tenant_id: str, account_type: str | None = None) -> list[AccountResponse]:
        accounts = await FinanceRepository.list_accounts(tenant_id, account_type)
        return [FinanceService._account_response(a) for a in accounts]

    @staticmethod
    async def get_account(tenant_id: str, account_id: str) -> AccountResponse:
        account = await FinanceRepository.get_account(tenant_id, account_id)
        if account is None:
            raise NotFoundError("Account not found")
        return FinanceService._account_response(account)

    @staticmethod
    async def create_account(tenant_id: str, data: AccountCreate, actor_id: str) -> AccountResponse:
        existing = await FinanceRepository.get_account_by_code(tenant_id, data.code)
        if existing:
            raise ConflictError(f"Account code '{data.code}' already exists")
        account = await FinanceRepository.create_account(tenant_id, data.model_dump())
        await AuditService.log_event(tenant_id, "finance.account_created", "account", str(account.id), actor_id)
        return FinanceService._account_response(account)

    @staticmethod
    async def update_account(
        tenant_id: str, account_id: str, data: AccountUpdate, actor_id: str
    ) -> AccountResponse:
        account = await FinanceRepository.get_account(tenant_id, account_id)
        if account is None:
            raise NotFoundError("Account not found")
        account = await FinanceRepository.update_account(account, data.model_dump(exclude_unset=True))
        await AuditService.log_event(tenant_id, "finance.account_updated", "account", str(account.id), actor_id)
        return FinanceService._account_response(account)

    @staticmethod
    async def delete_account(tenant_id: str, account_id: str, actor_id: str) -> None:
        account = await FinanceRepository.get_account(tenant_id, account_id)
        if account is None:
            raise NotFoundError("Account not found")
        await FinanceRepository.soft_delete_account(account)
        await AuditService.log_event(tenant_id, "finance.account_deleted", "account", str(account.id), actor_id)

    @staticmethod
    async def list_entries(tenant_id: str, account_id: str | None = None) -> list[JournalEntryResponse]:
        entries = await FinanceRepository.list_entries(tenant_id, account_id)
        return [
            JournalEntryResponse(
                id=str(e.id),
                account_id=str(e.account_id),
                entry_type=e.entry_type,
                amount=e.amount,
                description=e.description,
                reference=e.reference,
                posted_by=str(e.posted_by),
                posted_at=e.posted_at,
            )
            for e in entries
        ]

    @staticmethod
    async def post_entry(tenant_id: str, data: JournalEntryCreate, actor_id: str) -> JournalEntryResponse:
        account = await FinanceRepository.get_account(tenant_id, data.account_id)
        if account is None:
            raise NotFoundError("Account not found")

        if data.entry_type not in ("debit", "credit"):
            raise ValidationError("entry_type must be debit or credit")

        amount = abs(data.amount)
        if data.entry_type == "debit":
            account.balance += amount
        else:
            account.balance -= amount
        await account.touch()

        entry = await FinanceRepository.create_entry(
            tenant_id,
            {
                "account_id": PydanticObjectId(data.account_id),
                "entry_type": data.entry_type,
                "amount": amount,
                "description": data.description,
                "reference": data.reference,
                "posted_by": PydanticObjectId(actor_id),
            },
        )
        await AuditService.log_event(tenant_id, "finance.entry_posted", "journal_entry", str(entry.id), actor_id)
        return JournalEntryResponse(
            id=str(entry.id),
            account_id=str(entry.account_id),
            entry_type=entry.entry_type,
            amount=entry.amount,
            description=entry.description,
            reference=entry.reference,
            posted_by=str(entry.posted_by),
            posted_at=entry.posted_at,
        )
