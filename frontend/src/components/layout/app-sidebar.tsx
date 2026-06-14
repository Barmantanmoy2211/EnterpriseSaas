"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronLeft, ChevronRight, LogOut } from "lucide-react";

import { filterNavByPermissions, navSections } from "@/config/nav";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";
import { useUiStore } from "@/stores/ui-store";

export function AppSidebar() {
  const pathname = usePathname();
  const collapsed = useUiStore((s) => s.sidebarCollapsed);
  const toggle = useUiStore((s) => s.toggleSidebar);
  const user = useAuthStore((s) => s.user);
  const permissions = useAuthStore((s) => s.permissions);
  const isTenantAdmin = useAuthStore((s) => s.isTenantAdmin);
  const clearAuth = useAuthStore((s) => s.clearAuth);

  const sections = filterNavByPermissions(navSections, permissions, isTenantAdmin);
  const primaryRole = user?.roles?.[0];

  return (
    <aside
      className={cn(
        "flex h-full min-h-0 shrink-0 flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground transition-[width] duration-300",
        collapsed ? "w-[4.25rem]" : "w-64",
      )}
    >
      {/* Header — fixed */}
      <div className="flex h-14 shrink-0 items-center justify-between border-b border-sidebar-border px-3">
        {!collapsed && (
          <Link href="/dashboard" className="truncate text-base font-bold text-primary">
            EnterpriseOS
          </Link>
        )}
        <Button
          variant="ghost"
          size="icon"
          className="shrink-0 text-sidebar-foreground hover:bg-sidebar-accent"
          onClick={toggle}
          aria-label="Toggle sidebar"
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>

      {/* Nav — scrollable */}
      <nav className="sidebar-scroll min-h-0 flex-1 overflow-y-auto overflow-x-hidden px-2 py-3">
        <div className="space-y-4">
          {sections.map((section) => (
            <div key={section.id}>
              {!collapsed && (
                <p className="mb-1 px-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                  {section.label}
                </p>
              )}
              <ul className="space-y-0.5">
                {section.items.map((item) => {
                  const Icon = item.icon;
                  const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        title={collapsed ? item.label : undefined}
                        className={cn(
                          "flex items-center gap-3 rounded-md px-2.5 py-2 text-sm font-medium transition-colors",
                          active
                            ? "bg-primary text-primary-foreground shadow-sm"
                            : "text-muted-foreground hover:bg-sidebar-accent hover:text-foreground",
                          collapsed && "justify-center px-2",
                        )}
                      >
                        <Icon className="h-4 w-4 shrink-0" />
                        {!collapsed && <span className="truncate">{item.label}</span>}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>
      </nav>

      {/* Footer — fixed, always visible */}
      <div className="shrink-0 border-t border-sidebar-border p-3">
        {!collapsed && user && (
          <div className="mb-2 space-y-1 rounded-md bg-sidebar-accent/60 px-2.5 py-2">
            <p className="truncate text-sm font-medium">
              {user.first_name ? `${user.first_name} ${user.last_name}`.trim() : user.email}
            </p>
            <p className="truncate text-xs text-muted-foreground">{user.email}</p>
            {primaryRole && (
              <Badge variant="secondary" className="text-[10px] font-normal">
                {primaryRole.name}
              </Badge>
            )}
          </div>
        )}
        <Button
          variant="ghost"
          size={collapsed ? "icon" : "default"}
          className={cn(
            "w-full text-muted-foreground hover:bg-sidebar-accent hover:text-foreground",
            !collapsed && "justify-start gap-2",
          )}
          onClick={() => {
            clearAuth();
            window.location.href = "/login";
          }}
        >
          <LogOut className="h-4 w-4 shrink-0" />
          {!collapsed && <span>Sign out</span>}
        </Button>
      </div>
    </aside>
  );
}
