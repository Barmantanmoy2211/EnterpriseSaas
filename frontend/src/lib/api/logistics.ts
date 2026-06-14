import { api } from "./client";

export interface Shipment {
  id: string;
  shipment_number: string;
  origin: string;
  destination: string;
  carrier: string;
  tracking_number: string;
  status: string;
}

export const logisticsApi = {
  list: (token: string) => api.get<Shipment[]>("/api/v1/logistics/shipments", { token }),
  create: (token: string, data: Partial<Shipment> & { shipment_number: string }) =>
    api.post<Shipment>("/api/v1/logistics/shipments", data, { token }),
};
