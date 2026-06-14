import { api } from "./client";

export interface Bom {
  id: string;
  product_sku: string;
  name: string;
  description: string;
  version: number;
  is_active: boolean;
}

export interface ProductionOrder {
  id: string;
  order_number: string;
  bom_id: string;
  quantity: number;
  status: string;
}

export const manufacturingApi = {
  listBoms: (token: string) => api.get<Bom[]>("/api/v1/manufacturing/boms", { token }),
  listOrders: (token: string) => api.get<ProductionOrder[]>("/api/v1/manufacturing/orders", { token }),
  createBom: (token: string, data: Partial<Bom> & { product_sku: string; name: string }) =>
    api.post<Bom>("/api/v1/manufacturing/boms", data, { token }),
};
