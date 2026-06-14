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
          isTenantAdmin: false,
        }),
      hasPermission: (key: string) => {
        const state = get();
        if (state.isTenantAdmin) return true;
        return state.permissions.includes(key);
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
        isTenantAdmin: state.isTenantAdmin,
      }),
    },
  ),
);

export type { UserRole };
