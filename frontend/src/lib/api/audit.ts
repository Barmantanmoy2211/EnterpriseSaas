import { api } from "./client";

export interface AuditLog {
  id: string;
  user_id: string | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  details: Record<string, unknown>;
  ip_address: string | null;
  request_id: string | null;
  created_at: string;
}

export interface AuditLogListResponse {
  items: AuditLog[];
  total: number;
}

export const auditApi = {
  list: (token: string, params?: { resource_type?: string; limit?: number }) => {
    const qs = new URLSearchParams();
    if (params?.resource_type) qs.set("resource_type", params.resource_type);
    if (params?.limit) qs.set("limit", String(params.limit));
    const query = qs.toString();
    return api.get<AuditLogListResponse>(
      `/api/v1/audit/logs${query ? `?${query}` : ""}`,
      { token },
    );
  },
};
