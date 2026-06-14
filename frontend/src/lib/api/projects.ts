import { api } from "./client";

export interface Project {
  id: string;
  name: string;
  description: string;
  code: string;
  status: string;
  priority: string;
  owner_id: string | null;
  org_node_id: string | null;
  start_date: string | null;
  end_date: string | null;
  metadata: Record<string, unknown>;
}

export const projectsApi = {
  list: (token: string, status?: string) =>
    api.get<Project[]>(`/api/v1/projects${status ? `?status=${status}` : ""}`, { token }),

  get: (token: string, id: string) => api.get<Project>(`/api/v1/projects/${id}`, { token }),

  create: (token: string, data: Partial<Project> & { name: string }) =>
    api.post<Project>("/api/v1/projects", data, { token }),

  update: (token: string, id: string, data: Partial<Project>) =>
    api.patch<Project>(`/api/v1/projects/${id}`, data, { token }),

  delete: (token: string, id: string) => api.delete<void>(`/api/v1/projects/${id}`, { token }),
};
