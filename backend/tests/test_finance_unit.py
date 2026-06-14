"""Unit tests for finance schemas."""

from app.finance.schemas import AccountCreate, JournalEntryCreate


def test_account_create_defaults():
    a = AccountCreate(code="1000", name="Cash", account_type="asset")
    assert a.code == "1000"
    assert a.currency == "USD"
    assert a.is_active is True


def test_journal_entry_create():
    e = JournalEntryCreate(account_id="a1", entry_type="debit", amount=500)
    assert e.entry_type == "debit"
    assert e.amount == 500
