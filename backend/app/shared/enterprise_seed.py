"""Seed default enterprise module data for new tenants."""

from app.finance.repository import FinanceRepository
from app.inventory.repository import InventoryRepository


async def seed_enterprise_defaults(tenant_id: str, admin_user_id: str) -> None:
    existing_accounts = await FinanceRepository.list_accounts(tenant_id)
    if not existing_accounts:
        chart_of_accounts = [
            {"code": "1000", "name": "Cash", "account_type": "asset", "balance": 0},
            {"code": "1100", "name": "Accounts Receivable", "account_type": "asset", "balance": 0},
            {"code": "2000", "name": "Accounts Payable", "account_type": "liability", "balance": 0},
            {"code": "3000", "name": "Equity", "account_type": "equity", "balance": 0},
            {"code": "4000", "name": "Revenue", "account_type": "revenue", "balance": 0},
            {"code": "5000", "name": "Operating Expenses", "account_type": "expense", "balance": 0},
        ]
        for account in chart_of_accounts:
            await FinanceRepository.create_account(tenant_id, account)

    existing_items = await InventoryRepository.list_items(tenant_id)
    if not existing_items:
        sample_items = [
            {
                "sku": "RAW-001",
                "name": "Raw Material A",
                "description": "Primary raw material",
                "quantity": 100,
                "unit": "kg",
                "warehouse_location": "WH-A-01",
                "reorder_level": 20,
            },
            {
                "sku": "FG-001",
                "name": "Finished Good Alpha",
                "description": "Standard finished product",
                "quantity": 50,
                "unit": "ea",
                "warehouse_location": "WH-B-01",
                "reorder_level": 10,
            },
        ]
        for item in sample_items:
            await InventoryRepository.create_item(tenant_id, item)

    _ = admin_user_id  # reserved for future workflow seeds
