# Phase 4 — Enterprise Module Collections

MongoDB collections for Inventory, Resources, Finance, Procurement, Manufacturing, and Logistics.

## inventory_items / inventory_movements

Stock items with SKU, quantity, warehouse location, and reorder levels. Movements track in/out/adjust transactions with automatic quantity updates.

## resources / resource_allocations

Equipment, facilities, and capacity resources with project-linked allocations over date ranges.

## accounts / journal_entries

Chart of accounts with debit/credit journal entries that update account balances.

## suppliers / purchase_orders

Vendor master data and purchase orders with line items and computed totals.

## bills_of_materials / production_orders

Product BOMs with component lists and production orders linked to BOMs.

## shipments

Logistics shipments with origin/destination, carrier, tracking, and optional PO linkage.
