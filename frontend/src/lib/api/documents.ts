import { api } from "./client";

export interface Document {
  id: string;
  title: string;
  description: string;
  file_url: string;
  mime_type: string;
  size_bytes: number;
  folder_path: string;
  uploaded_by: string;
  tags: string[];
  version: number;
}

export const documentsApi = {
  list: (token: string, folder_path?: string) =>
    api.get<Document[]>(
      `/api/v1/documents${folder_path ? `?folder_path=${encodeURIComponent(folder_path)}` : ""}`,
      { token },
    ),

  create: (token: string, data: Partial<Document> & { title: string }) =>
    api.post<Document>("/api/v1/documents", data, { token }),

  delete: (token: string, id: string) => api.delete<void>(`/api/v1/documents/${id}`, { token }),
};
