import { api } from "./client";

export interface SavedReport {
  id: string;
  name: string;
  description: string;
  entity_type: string;
  filters: Record<string, unknown>;
  columns: string[];
  created_by: string;
  is_shared: boolean;
}

export interface ReportRun {
  id: string;
  report_id: string;
  run_by: string;
  row_count: number;
  result_preview: Record<string, unknown>[];
  run_at: string;
}

export const reportsApi = {
  list: (token: string) => api.get<SavedReport[]>("/api/v1/reports", { token }),

  create: (token: string, data: Partial<SavedReport> & { name: string; entity_type: string }) =>
    api.post<SavedReport>("/api/v1/reports", data, { token }),

  run: (token: string, id: string) => api.post<ReportRun>(`/api/v1/reports/${id}/run`, {}, { token }),
};
