import { api } from "./client";

export interface Job {
  id: string;
  title: string;
  description: string;
  org_node_id: string | null;
  status: string;
  requirements: string[];
  location: string;
  employment_type: string;
}

export interface Candidate {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  resume_url: string | null;
  source: string;
}

export interface Application {
  id: string;
  job_id: string;
  candidate_id: string;
  status: string;
  notes: string;
  stage_history: Array<Record<string, unknown>>;
}

export const recruitmentApi = {
  listJobs: (token: string, status?: string) =>
    api.get<Job[]>(`/api/v1/recruitment/jobs${status ? `?status=${status}` : ""}`, { token }),

  createJob: (token: string, data: { title: string; description?: string; location?: string }) =>
    api.post<Job>("/api/v1/recruitment/jobs", data, { token }),

  listCandidates: (token: string) =>
    api.get<Candidate[]>("/api/v1/recruitment/candidates", { token }),

  createCandidate: (
    token: string,
    data: { first_name: string; last_name: string; email: string; phone?: string },
  ) => api.post<Candidate>("/api/v1/recruitment/candidates", data, { token }),

  listApplications: (token: string, jobId?: string) =>
    api.get<Application[]>(
      `/api/v1/recruitment/applications${jobId ? `?job_id=${jobId}` : ""}`,
      { token },
    ),

  createApplication: (token: string, data: { job_id: string; candidate_id: string }) =>
    api.post<Application>("/api/v1/recruitment/applications", data, { token }),

  updateApplication: (token: string, id: string, data: { status?: string }) =>
    api.patch<Application>(`/api/v1/recruitment/applications/${id}`, data, { token }),
};
