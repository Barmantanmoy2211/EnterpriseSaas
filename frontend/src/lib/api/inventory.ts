import { api } from "./client";

export interface InventoryItem {
  id: string;
  sku: string;
  name: string;
  description: string;
  quantity: number;
  unit: string;
  warehouse_location: string;
  reorder_level: number;
  status: string;
}

export const inventoryApi = {
  list: (token: string) => api.get<InventoryItem[]>("/api/v1/inventory/items", { token }),
  create: (token: string, data: Partial<InventoryItem> & { sku: string; name: string }) =>
    api.post<InventoryItem>("/api/v1/inventory/items", data, { token }),
  recordMovement: (token: string, data: { item_id: string; movement_type: string; quantity: number }) =>
    api.post("/api/v1/inventory/movements", data, { token }),
};
