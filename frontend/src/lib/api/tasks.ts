import { api } from "./client";

export interface Task {
  id: string;
  title: string;
  description: string;
  project_id: string | null;
  assignee_id: string | null;
  created_by: string;
  status: string;
  priority: string;
  due_date: string | null;
  tags: string[];
  metadata: Record<string, unknown>;
}

export const tasksApi = {
  list: (token: string, params?: { project_id?: string; status?: string }) => {
    const qs = new URLSearchParams();
    if (params?.project_id) qs.set("project_id", params.project_id);
    if (params?.status) qs.set("status", params.status);
    const query = qs.toString();
    return api.get<Task[]>(`/api/v1/tasks${query ? `?${query}` : ""}`, { token });
  },

  create: (token: string, data: Partial<Task> & { title: string }) =>
    api.post<Task>("/api/v1/tasks", data, { token }),

  update: (token: string, id: string, data: Partial<Task>) =>
    api.patch<Task>(`/api/v1/tasks/${id}`, data, { token }),

  delete: (token: string, id: string) => api.delete<void>(`/api/v1/tasks/${id}`, { token }),
};
