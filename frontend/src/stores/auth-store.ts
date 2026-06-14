"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { User, UserRole } from "@/lib/api/auth";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  tenantSlug: string | null;
  permissions: string[];
  scopeNodeIds: string[];
  isTenantAdmin: boolean;
  setAuth: (
    tokens: { access_token: string; refresh_token: string },
    user: User,
    tenantSlug?: string,
  ) => void;
  setUserContext: (user: User) => void;
  clearAuth: () => void;
  hasPermission: (key: string) => boolean;
}

function extractAuthMeta(user: User) {
  return {
    user,
    permissions: user.permissions ?? [],
    scopeNodeIds: user.scope_node_ids ?? [],
    isTenantAdmin: user.is_tenant_admin ?? user.roles?.some((r) => r.code === "tenant_admin") ?? false,
  };
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      tenantSlug: null,
      permissions: [],
      scopeNodeIds: [],
      isTenantAdmin: false,
      setAuth: (tokens, user, tenantSlug) =>
        set({
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
          tenantSlug: tenantSlug ?? null,
          ...extractAuthMeta(user),
        }),
      setUserContext: (user) => set(extractAuthMeta(user)),
      clearAuth: () =>
        set({
          accessToken: null,
          refreshToken: null,
          user: null,
          tenantSlug: null,
          permissions: [],
          scopeNodeIds: [],
          isTenantAdmin: false,
        }),
      hasPermission: (key: string) => {
        const state = get();
        if (state.isTenantAdmin) return true;
        if (state.permissions.includes(key)) return true;
        const [resource, action] = key.split(":");
        if (!resource || !action) return false;
        const aliases: Record<string, string[]> = {
          manage: ["create", "update", "edit", "manage", "delete"],
          create: ["create", "manage"],
          update: ["update", "edit", "manage"],
          edit: ["edit", "update", "manage"],
          delete: ["delete", "manage"],
          settings: ["settings", "manage", "update", "edit"],
          manage_types: ["manage_types", "manage", "create", "update"],
          action: ["action", "manage"],
          request: ["request", "manage"],
        };
        const acceptable = aliases[action] ?? [action];
        return acceptable.some((a) => state.permissions.includes(`${resource}:${a}`));
      },
    }),
    {
      name: "enterpriseos-auth",
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
        tenantSlug: state.tenantSlug,
        permissions: state.permissions,
        scopeNodeIds: state.scopeNodeIds,
        isTenantAdmin: state.isTenantAdmin,
      }),
    },
  ),
);

export type { UserRole };
