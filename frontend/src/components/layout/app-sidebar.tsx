"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Building2,
  Calendar,
  CalendarDays,
  CheckSquare,
  ChevronLeft,
  ChevronRight,
  Clock,
  Cpu,
  Factory,
  FileStack,
  FileText,
  FolderKanban,
  GitBranch,
  Landmark,
  LayoutDashboard,
  LineChart,
  ListTodo,
  LogOut,
  MessageSquare,
  Package,
  Settings,
  Shield,
  Ship,
  ShoppingCart,
  Star,
  UserPlus,
  Users,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";
import { useUiStore } from "@/stores/ui-store";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/organization", label: "Organization", icon: Building2 },
  { href: "/employees", label: "Employees", icon: Users },
  { href: "/recruitment", label: "Recruitment", icon: UserPlus },
  { href: "/leave", label: "Leave", icon: Calendar },
  { href: "/attendance", label: "Attendance", icon: Clock },
  { href: "/performance", label: "Performance", icon: Star },
  { href: "/projects", label: "Projects", icon: FolderKanban },
  { href: "/tasks", label: "Tasks", icon: ListTodo },
  { href: "/calendar", label: "Calendar", icon: CalendarDays },
  { href: "/documents", label: "Documents", icon: FileStack },
  { href: "/communication", label: "Communication", icon: MessageSquare },
  { href: "/reports", label: "Reports", icon: BarChart3 },
  { href: "/analytics", label: "Analytics", icon: LineChart },
  { href: "/inventory", label: "Inventory", icon: Package },
  { href: "/resources", label: "Resources", icon: Cpu },
  { href: "/finance", label: "Finance", icon: Landmark },
  { href: "/procurement", label: "Procurement", icon: ShoppingCart },
  { href: "/manufacturing", label: "Manufacturing", icon: Factory },
  { href: "/logistics", label: "Logistics", icon: Ship },
  { href: "/approvals", label: "Approvals", icon: CheckSquare },
  { href: "/workflows", label: "Workflows", icon: GitBranch },
  { href: "/audit", label: "Audit Log", icon: FileText },
  { href: "/settings/roles", label: "Roles", icon: Shield },
  { href: "/settings/tenant", label: "Settings", icon: Settings },
];

export function AppSidebar() {
  const pathname = usePathname();
  const collapsed = useUiStore((s) => s.sidebarCollapsed);
  const toggle = useUiStore((s) => s.toggleSidebar);
  const user = useAuthStore((s) => s.user);
  const clearAuth = useAuthStore((s) => s.clearAuth);

  return (
    <aside
      className={cn(
        "flex h-screen flex-col border-r bg-card transition-all duration-300",
        collapsed ? "w-16" : "w-64",
      )}
    >
      <div className="flex h-16 items-center justify-between border-b px-4">
        {!collapsed && (
          <Link href="/dashboard" className="text-lg font-bold text-primary">
            EnterpriseOS
          </Link>
        )}
        <Button variant="ghost" size="icon" onClick={toggle} aria-label="Toggle sidebar">
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>

      <nav className="flex-1 space-y-1 p-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
              )}
            >
              <Icon className="h-5 w-5 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      <div className="border-t p-4">
        {!collapsed && user && (
          <div className="mb-3 truncate text-sm">
            <p className="font-medium">{user.first_name || user.email}</p>
            <p className="text-xs text-muted-foreground">{user.email}</p>
          </div>
        )}
        <Button
          variant="ghost"
          className={cn("w-full", collapsed ? "px-0" : "justify-start")}
          onClick={() => {
            clearAuth();
            window.location.href = "/login";
          }}
        >
          <LogOut className="h-4 w-4" />
          {!collapsed && <span>Sign out</span>}
        </Button>
      </div>
    </aside>
  );
}
