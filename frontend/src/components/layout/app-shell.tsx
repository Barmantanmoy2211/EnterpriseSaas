"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { AppSidebar } from "@/components/layout/app-sidebar";
import { GlobalSearch } from "@/components/layout/global-search";
import { NotificationBell } from "@/components/layout/notification-bell";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { authApi } from "@/lib/api/auth";
import { useAuthStore } from "@/stores/auth-store";

export function AppShell({ children, title }: { children: React.ReactNode; title?: string }) {
  const router = useRouter();
  const accessToken = useAuthStore((s) => s.accessToken);
  const setUserContext = useAuthStore((s) => s.setUserContext);

  useEffect(() => {
    if (!accessToken) {
      router.replace("/login");
      return;
    }
    authApi.me(accessToken).then(setUserContext).catch(() => {});
  }, [accessToken, router, setUserContext]);

  if (!accessToken) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  return (
    <div className="flex h-screen min-h-0 overflow-hidden bg-background">
      <AppSidebar />
      <div className="flex min-h-0 min-w-0 flex-1 flex-col">
        <header className="flex h-14 shrink-0 items-center gap-4 border-b bg-card px-4 sm:px-6">
          {title && <h1 className="truncate text-lg font-semibold sm:text-xl">{title}</h1>}
          <div className="ml-auto flex items-center gap-2">
            <GlobalSearch />
            <NotificationBell />
            <ThemeToggle />
          </div>
        </header>
        <main className="min-h-0 flex-1 overflow-auto p-4 sm:p-6">{children}</main>
      </div>
    </div>
  );
}
