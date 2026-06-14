import { api } from "./client";

export interface PerformanceReview {
  id: string;
  employee_id: string;
  reviewer_id: string;
  period: string;
  rating: number | null;
  feedback: string;
  goals_summary: string;
  status: string;
}

export interface PerformanceGoal {
  id: string;
  employee_id: string;
  title: string;
  description: string;
  target_date: string | null;
  status: string;
  progress: number;
}

export interface TrainingCourse {
  id: string;
  title: string;
  description: string;
  duration_hours: number;
  is_mandatory: boolean;
  category: string;
}

export const performanceApi = {
  listReviews: (token: string, employeeId?: string) =>
    api.get<PerformanceReview[]>(
      `/api/v1/performance/reviews${employeeId ? `?employee_id=${employeeId}` : ""}`,
      { token },
    ),

  createReview: (
    token: string,
    data: { employee_id: string; period: string; rating?: number; feedback?: string },
  ) => api.post<PerformanceReview>("/api/v1/performance/reviews", data, { token }),

  listGoals: (token: string, employeeId?: string) =>
    api.get<PerformanceGoal[]>(
      `/api/v1/performance/goals${employeeId ? `?employee_id=${employeeId}` : ""}`,
      { token },
    ),

  createGoal: (token: string, data: { employee_id: string; title: string; description?: string }) =>
    api.post<PerformanceGoal>("/api/v1/performance/goals", data, { token }),

  listCourses: (token: string) => api.get<TrainingCourse[]>("/api/v1/training/courses", { token }),

  createCourse: (token: string, data: { title: string; description?: string }) =>
    api.post<TrainingCourse>("/api/v1/training/courses", data, { token }),
};
