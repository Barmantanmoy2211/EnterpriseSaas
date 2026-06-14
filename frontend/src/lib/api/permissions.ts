import { api } from "./client";

export interface Permission {
  id: string;
  resource: string;
  action: string;
  description: string;
  conditions: Record<string, unknown>;
}

export interface Role {
  id: string;
  code: string;
  name: string;
  description: string;
  is_system: boolean;
  permission_ids: string[];
}

export interface RoleAssignment {
  id: string;
  user_id: string;
  role_id: string;
  scope_node_id: string | null;
}

export const permissionsApi = {
  listPermissions: (token: string) =>
    api.get<Permission[]>("/api/v1/permissions", { token }),

  listRoles: (token: string) => api.get<Role[]>("/api/v1/permissions/roles", { token }),

  createRole: (
    token: string,
    data: { code: string; name: string; description?: string; permission_ids: string[] },
  ) => api.post<Role>("/api/v1/permissions/roles", data, { token }),

  updateRole: (
    token: string,
    roleId: string,
    data: { name?: string; description?: string; permission_ids?: string[] },
  ) => api.patch<Role>(`/api/v1/permissions/roles/${roleId}`, data, { token }),

  listAssignments: (token: string) =>
    api.get<RoleAssignment[]>("/api/v1/permissions/assignments", { token }),

  createAssignment: (
    token: string,
    data: { user_id: string; role_id: string; scope_node_id?: string | null },
  ) => api.post<RoleAssignment>("/api/v1/permissions/assignments", data, { token }),

  deleteAssignment: (token: string, assignmentId: string) =>
    api.delete<void>(`/api/v1/permissions/assignments/${assignmentId}`, { token }),
};
