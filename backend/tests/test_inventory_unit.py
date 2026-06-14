"""Unit tests for inventory schemas."""

from app.inventory.schemas import InventoryItemCreate, InventoryMovementCreate


def test_inventory_item_create_defaults():
    item = InventoryItemCreate(sku="SKU-001", name="Widget")
    assert item.sku == "SKU-001"
    assert item.quantity == 0
    assert item.unit == "ea"


def test_inventory_movement_create():
    m = InventoryMovementCreate(item_id="abc", movement_type="in", quantity=10)
    assert m.movement_type == "in"
    assert m.quantity == 10
