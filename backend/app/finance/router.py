from fastapi import APIRouter, Depends, Query, status

from app.finance.schemas import (
    AccountCreate,
    AccountResponse,
    AccountUpdate,
    JournalEntryCreate,
    JournalEntryResponse,
)
from app.finance.service import FinanceService
from app.permissions.dependencies import require_permission

router = APIRouter(prefix="/finance", tags=["finance"])


@router.get("/accounts", response_model=list[AccountResponse])
async def list_accounts(
    account_type: str | None = Query(None),
    user=Depends(require_permission("finance", "read")),
):
    return await FinanceService.list_accounts(str(user.tenant_id), account_type)


@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(account_id: str, user=Depends(require_permission("finance", "read"))):
    return await FinanceService.get_account(str(user.tenant_id), account_id)


@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    data: AccountCreate,
    user=Depends(require_permission("finance", "manage")),
):
    return await FinanceService.create_account(str(user.tenant_id), data, str(user.id))


@router.patch("/accounts/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: str,
    data: AccountUpdate,
    user=Depends(require_permission("finance", "manage")),
):
    return await FinanceService.update_account(str(user.tenant_id), account_id, data, str(user.id))


@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: str,
    user=Depends(require_permission("finance", "manage")),
):
    await FinanceService.delete_account(str(user.tenant_id), account_id, str(user.id))


@router.get("/entries", response_model=list[JournalEntryResponse])
async def list_entries(
    account_id: str | None = Query(None),
    user=Depends(require_permission("finance", "read")),
):
    return await FinanceService.list_entries(str(user.tenant_id), account_id)


@router.post("/entries", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def post_entry(
    data: JournalEntryCreate,
    user=Depends(require_permission("finance", "manage")),
):
    return await FinanceService.post_entry(str(user.tenant_id), data, str(user.id))
