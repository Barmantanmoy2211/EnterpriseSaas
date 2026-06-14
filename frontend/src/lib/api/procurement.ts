import { api } from "./client";

export interface Supplier {
  id: string;
  name: string;
  code: string;
  contact_name: string;
  contact_email: string;
  status: string;
}

export interface PurchaseOrder {
  id: string;
  po_number: string;
  supplier_id: string;
  status: string;
  total_amount: number;
  currency: string;
}

export const procurementApi = {
  listSuppliers: (token: string) => api.get<Supplier[]>("/api/v1/procurement/suppliers", { token }),
  listOrders: (token: string) => api.get<PurchaseOrder[]>("/api/v1/procurement/orders", { token }),
  createSupplier: (token: string, data: Partial<Supplier> & { name: string }) =>
    api.post<Supplier>("/api/v1/procurement/suppliers", data, { token }),
};
