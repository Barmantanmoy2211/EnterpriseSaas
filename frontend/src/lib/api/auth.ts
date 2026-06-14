import { api } from "./client";

export interface UserRole {
  code: string;
  name: string;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  status: string;
  tenant_id: string;
  roles?: UserRole[];
  permissions?: string[];
  is_tenant_admin?: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthResponse {
  tokens: TokenResponse;
  user: User;
}

export interface RegisterData {
  tenant_name: string;
  tenant_slug: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface LoginData {
  email: string;
  password: string;
  tenant_slug?: string;
}

export const authApi = {
  register: (data: RegisterData) =>
    api.post<AuthResponse>("/api/v1/auth/register", data),

  login: (data: LoginData) => api.post<AuthResponse>("/api/v1/auth/login", data),

  refresh: (refresh_token: string) =>
    api.post<TokenResponse>("/api/v1/auth/refresh", { refresh_token }),

  logout: (token: string) =>
    api.post<void>("/api/v1/auth/logout", undefined, { token }),

  me: (token: string) => api.get<User>("/api/v1/auth/me", { token }),

  listUsers: (token: string) => api.get<User[]>("/api/v1/auth/users", { token }),
};
