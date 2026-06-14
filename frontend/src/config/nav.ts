import type { LucideIcon } from "lucide-react";
import {
  BarChart3,
  Building2,
  Calendar,
  CalendarDays,
  CheckSquare,
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

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  /** Permission key e.g. "employee:read" — omit for always visible */
  permission?: string;
}

export interface NavSection {
  id: string;
  label: string;
  items: NavItem[];
}

export const navSections: NavSection[] = [
  {
    id: "core",
    label: "Core",
    items: [
      { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
      { href: "/organization", label: "Organization", icon: Building2, permission: "org:read" },
    ],
  },
  {
    id: "hr",
    label: "HR",
    items: [
      { href: "/employees", label: "Employees", icon: Users, permission: "employee:read" },
      { href: "/recruitment", label: "Recruitment", icon: UserPlus, permission: "recruitment:read" },
      { href: "/leave", label: "Leave", icon: Calendar, permission: "leave:read" },
      { href: "/attendance", label: "Attendance", icon: Clock, permission: "attendance:read" },
      { href: "/performance", label: "Performance", icon: Star, permission: "performance:read" },
    ],
  },
  {
    id: "operations",
    label: "Operations",
    items: [
      { href: "/projects", label: "Projects", icon: FolderKanban, permission: "project:read" },
      { href: "/tasks", label: "Tasks", icon: ListTodo, permission: "task:read" },
      { href: "/calendar", label: "Calendar", icon: CalendarDays, permission: "calendar:read" },
      { href: "/documents", label: "Documents", icon: FileStack, permission: "document:read" },
      { href: "/communication", label: "Communication", icon: MessageSquare, permission: "communication:read" },
      { href: "/reports", label: "Reports", icon: BarChart3, permission: "report:read" },
      { href: "/analytics", label: "Analytics", icon: LineChart, permission: "analytics:read" },
    ],
  },
  {
    id: "enterprise",
    label: "Enterprise",
    items: [
      { href: "/inventory", label: "Inventory", icon: Package, permission: "inventory:read" },
      { href: "/resources", label: "Resources", icon: Cpu, permission: "resource:read" },
      { href: "/finance", label: "Finance", icon: Landmark, permission: "finance:read" },
      { href: "/procurement", label: "Procurement", icon: ShoppingCart, permission: "procurement:read" },
      { href: "/manufacturing", label: "Manufacturing", icon: Factory, permission: "manufacturing:read" },
      { href: "/logistics", label: "Logistics", icon: Ship, permission: "logistics:read" },
    ],
  },
  {
    id: "platform",
    label: "Platform",
    items: [
      { href: "/approvals", label: "Approvals", icon: CheckSquare, permission: "approval:read" },
      { href: "/workflows", label: "Workflows", icon: GitBranch, permission: "workflow:read" },
      { href: "/audit", label: "Audit Log", icon: FileText, permission: "audit:read" },
    ],
  },
  {
    id: "admin",
    label: "Admin",
    items: [
      { href: "/settings/roles", label: "Roles", icon: Shield, permission: "role:read" },
      { href: "/settings/tenant", label: "Settings", icon: Settings, permission: "tenant:settings" },
    ],
  },
];

export function filterNavByPermissions(
  sections: NavSection[],
  permissions: string[],
  isAdmin: boolean,
): NavSection[] {
  if (isAdmin) return sections;

  const permSet = new Set(permissions);
  return sections
    .map((section) => ({
      ...section,
      items: section.items.filter((item) => !item.permission || permSet.has(item.permission)),
    }))
    .filter((section) => section.items.length > 0);
}
