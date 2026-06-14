import { api } from "./client";

export interface WorkflowDefinition {
  id: string;
  code: string;
  name: string;
  description: string;
  entity_type: string;
  steps: Array<{ id: string; name: string; type: string; config: Record<string, unknown> }>;
  is_active: boolean;
}

export interface WorkflowInstance {
  id: string;
  definition_id: string;
  entity_type: string;
  entity_id: string;
  current_step_id: string | null;
  status: string;
  context: Record<string, unknown>;
  history: Array<Record<string, unknown>>;
  initiated_by: string;
}

export const workflowsApi = {
  listDefinitions: (token: string) =>
    api.get<WorkflowDefinition[]>("/api/v1/workflows/definitions", { token }),

  createDefinition: (
    token: string,
    data: {
      code: string;
      name: string;
      description?: string;
      entity_type: string;
      steps: WorkflowDefinition["steps"];
    },
  ) => api.post<WorkflowDefinition>("/api/v1/workflows/definitions", data, { token }),

  listInstances: (token: string, status?: string) =>
    api.get<WorkflowInstance[]>(
      `/api/v1/workflows/instances${status ? `?status=${status}` : ""}`,
      { token },
    ),

  startInstance: (
    token: string,
    data: {
      definition_code: string;
      entity_type: string;
      entity_id: string;
      context?: Record<string, unknown>;
      scope_node_id?: string;
    },
  ) => api.post<WorkflowInstance>("/api/v1/workflows/instances", data, { token }),
};
