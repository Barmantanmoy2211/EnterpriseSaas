import { api } from "./client";

export interface OrgNodeType {
  id: string;
  code: string;
  label: string;
  allowed_child_types: string[];
  schema: Record<string, unknown>;
  is_root_allowed: boolean;
}

export interface OrgNode {
  id: string;
  parent_id: string | null;
  node_type: string;
  name: string;
  metadata: Record<string, unknown>;
  path: string[];
  depth: number;
  sort_order: number;
  children: OrgNode[];
}

export const organizationApi = {
  listNodeTypes: (token: string) =>
    api.get<OrgNodeType[]>("/api/v1/organization/node-types", { token }),

  createNodeType: (token: string, data: Omit<OrgNodeType, "id">) =>
    api.post<OrgNodeType>("/api/v1/organization/node-types", data, { token }),

  updateNodeType: (
    token: string,
    typeId: string,
    data: Partial<Omit<OrgNodeType, "id" | "code">>,
  ) => api.patch<OrgNodeType>(`/api/v1/organization/node-types/${typeId}`, data, { token }),

  deleteNodeType: (token: string, typeId: string) =>
    api.delete<void>(`/api/v1/organization/node-types/${typeId}`, { token }),

  getTree: (token: string) =>
    api.get<OrgNode[]>("/api/v1/organization/nodes/tree", { token }),

  createNode: (
    token: string,
    data: {
      parent_id?: string | null;
      node_type: string;
      name: string;
      metadata?: Record<string, unknown>;
      sort_order?: number;
    },
  ) => api.post<OrgNode>("/api/v1/organization/nodes", data, { token }),

  updateNode: (
    token: string,
    nodeId: string,
    data: { name?: string; metadata?: Record<string, unknown>; sort_order?: number },
  ) => api.patch<OrgNode>(`/api/v1/organization/nodes/${nodeId}`, data, { token }),

  moveNode: (token: string, nodeId: string, parent_id: string | null) =>
    api.post<OrgNode>(`/api/v1/organization/nodes/${nodeId}/move`, { parent_id }, { token }),

  deleteNode: (token: string, nodeId: string) =>
    api.delete<void>(`/api/v1/organization/nodes/${nodeId}`, { token }),
};
