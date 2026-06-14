import { api } from "./client";

export interface Approval {
  id: string;
  workflow_instance_id: string | null;
  step_id: string | null;
  requester_id: string;
  approver_id: string | null;
  scope_node_id: string | null;
  title: string;
  description: string;
  status: string;
  comments: string;
  entity_type: string;
  entity_id: string;
  created_at: string;
}

export const approvalsApi = {
  listPending: (token: string) =>
    api.get<Approval[]>("/api/v1/approvals/pending", { token }),

  listMine: (token: string) => api.get<Approval[]>("/api/v1/approvals/mine", { token }),

  get: (token: string, id: string) =>
    api.get<Approval>(`/api/v1/approvals/${id}`, { token }),

  approve: (token: string, id: string, comments = "") =>
    api.post<Approval>(`/api/v1/approvals/${id}/approve`, { comments }, { token }),

  reject: (token: string, id: string, comments = "") =>
    api.post<Approval>(`/api/v1/approvals/${id}/reject`, { comments }, { token }),

  create: (
    token: string,
    data: {
      title: string;
      description?: string;
      approver_id: string;
      entity_type?: string;
      entity_id?: string;
      scope_node_id?: string;
    },
  ) => api.post<Approval>("/api/v1/approvals", data, { token }),
};
