"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { User } from "@/lib/api/auth";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  tenantSlug: string | null;
  setAuth: (tokens: { access_token: string; refresh_token: string }, user: User, tenantSlug?: string) => void;
  clearAuth: () => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      tenantSlug: null,
      setAuth: (tokens, user, tenantSlug) =>
        set({
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
          user,
          tenantSlug: tenantSlug ?? null,
        }),
      clearAuth: () =>
        set({ accessToken: null, refreshToken: null, user: null, tenantSlug: null }),
      setUser: (user) => set({ user }),
    }),
    { name: "enterpriseos-auth" },
  ),
);
