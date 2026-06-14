import { api } from "./client";

export interface Tenant {
  id: string;
  slug: string;
  name: string;
  status: string;
  plan: string;
}

export interface TenantSettings {
  branding: {
    primary_color?: string;
    logo_url?: string;
  };
  auth_policy: Record<string, unknown>;
  org_defaults: Record<string, unknown>;
}

export const tenantApi = {
  getMe: (token: string) => api.get<Tenant>("/api/v1/tenants/me", { token }),

  updateMe: (token: string, data: { name?: string }) =>
    api.patch<Tenant>("/api/v1/tenants/me", data, { token }),

  getSettings: (token: string) =>
    api.get<TenantSettings>("/api/v1/tenants/me/settings", { token }),

  updateSettings: (token: string, data: Partial<TenantSettings>) =>
    api.patch<TenantSettings>("/api/v1/tenants/me/settings", data, { token }),
};
