import { api } from "./client";

export interface SearchResult {
  entity_type: string;
  entity_id: string;
  title: string;
  body: string;
  metadata: Record<string, unknown>;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total: number;
}

export const searchApi = {
  search: (token: string, q: string) =>
    api.get<SearchResponse>(`/api/v1/search?q=${encodeURIComponent(q)}`, { token }),

  reindex: (token: string) =>
    api.post<{ indexed: number }>("/api/v1/search/reindex", undefined, { token }),
};
