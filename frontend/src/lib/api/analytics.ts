import { api } from "./client";

export interface AnalyticsOverview {
  employees: Record<string, number>;
  projects: Record<string, number>;
  tasks: Record<string, number>;
  recruitment: Record<string, number>;
  approvals: Record<string, number>;
  totals: Record<string, number>;
}

export const analyticsApi = {
  overview: (token: string) => api.get<AnalyticsOverview>("/api/v1/analytics/overview", { token }),

  trends: (token: string, entity_type: string, days = 30) =>
    api.get<{ entity_type: string; daily_counts: { date: string; count: number }[] }>(
      `/api/v1/analytics/trends?entity_type=${entity_type}&days=${days}`,
      { token },
    ),
};
