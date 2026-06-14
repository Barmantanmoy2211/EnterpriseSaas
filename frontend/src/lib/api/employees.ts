import { api } from "./client";

export interface Employee {
  id: string;
  user_id: string | null;
  employee_code: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  org_node_id: string | null;
  job_title: string;
  department: string;
  employment_type: string;
  status: string;
  hire_date: string | null;
  manager_id: string | null;
  profile: Record<string, unknown>;
}

export const employeesApi = {
  list: (token: string, status?: string) =>
    api.get<Employee[]>(`/api/v1/employees${status ? `?status=${status}` : ""}`, { token }),

  get: (token: string, id: string) => api.get<Employee>(`/api/v1/employees/${id}`, { token }),

  create: (token: string, data: Partial<Employee> & { employee_code: string; first_name: string; last_name: string; email: string }) =>
    api.post<Employee>("/api/v1/employees", data, { token }),

  update: (token: string, id: string, data: Partial<Employee>) =>
    api.patch<Employee>(`/api/v1/employees/${id}`, data, { token }),

  delete: (token: string, id: string) =>
    api.delete<void>(`/api/v1/employees/${id}`, { token }),
};
