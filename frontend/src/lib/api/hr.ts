import { api } from "./client";

export interface LeaveType {
  id: string;
  code: string;
  name: string;
  days_allowed: number;
  is_paid: boolean;
}

export interface LeaveRequest {
  id: string;
  employee_id: string;
  leave_type_id: string;
  start_date: string;
  end_date: string;
  days: number;
  reason: string;
  status: string;
  workflow_instance_id: string | null;
}

export interface AttendanceRecord {
  id: string;
  employee_id: string;
  date: string;
  check_in: string | null;
  check_out: string | null;
  status: string;
  notes: string;
  hours_worked: number;
}

export const leaveApi = {
  listTypes: (token: string) => api.get<LeaveType[]>("/api/v1/leave/types", { token }),

  listRequests: (token: string, employeeId?: string) =>
    api.get<LeaveRequest[]>(
      `/api/v1/leave/requests${employeeId ? `?employee_id=${employeeId}` : ""}`,
      { token },
    ),

  createRequest: (
    token: string,
    data: {
      employee_id: string;
      leave_type_id: string;
      start_date: string;
      end_date: string;
      days: number;
      reason?: string;
    },
  ) => api.post<LeaveRequest>("/api/v1/leave/requests", data, { token }),
};

export const attendanceApi = {
  list: (token: string, employeeId?: string) =>
    api.get<AttendanceRecord[]>(
      `/api/v1/attendance/records${employeeId ? `?employee_id=${employeeId}` : ""}`,
      { token },
    ),

  checkIn: (token: string, employeeId: string) =>
    api.post<AttendanceRecord>("/api/v1/attendance/check-in", { employee_id: employeeId }, { token }),

  checkOut: (token: string, employeeId: string) =>
    api.post<AttendanceRecord>("/api/v1/attendance/check-out", { employee_id: employeeId }, { token }),
};
