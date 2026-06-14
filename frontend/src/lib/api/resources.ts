import { api } from "./client";

export interface Resource {
  id: string;
  name: string;
  resource_type: string;
  description: string;
  capacity: number;
  capacity_unit: string;
  status: string;
}

export const resourcesApi = {
  list: (token: string) => api.get<Resource[]>("/api/v1/resources", { token }),
  create: (token: string, data: Partial<Resource> & { name: string }) =>
    api.post<Resource>("/api/v1/resources", data, { token }),
};
