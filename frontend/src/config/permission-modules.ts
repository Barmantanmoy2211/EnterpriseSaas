/** Module labels for the permission matrix UI (must match backend PERMISSION_MODULES). */

export const PERMISSION_MODULES: { code: string; label: string }[] = [
  { code: "org", label: "Organization" },
  { code: "employee", label: "Employees" },
  { code: "recruitment", label: "Recruitment" },
  { code: "leave", label: "Leave" },
  { code: "attendance", label: "Attendance" },
  { code: "performance", label: "Performance" },
  { code: "training", label: "Training" },
  { code: "onboarding", label: "Onboarding" },
  { code: "exit", label: "Exit & Offboarding" },
  { code: "project", label: "Projects" },
  { code: "task", label: "Tasks" },
  { code: "calendar", label: "Calendar" },
  { code: "document", label: "Documents" },
  { code: "communication", label: "Communication" },
  { code: "report", label: "Reports" },
  { code: "analytics", label: "Analytics" },
  { code: "inventory", label: "Inventory" },
  { code: "resource", label: "Resources" },
  { code: "finance", label: "Finance" },
  { code: "procurement", label: "Procurement" },
  { code: "manufacturing", label: "Manufacturing" },
  { code: "logistics", label: "Logistics" },
  { code: "approval", label: "Approvals" },
  { code: "workflow", label: "Workflows" },
  { code: "audit", label: "Audit Log" },
  { code: "notification", label: "Notifications" },
  { code: "search", label: "Search" },
  { code: "user", label: "Users" },
  { code: "role", label: "Roles" },
  { code: "tenant", label: "Tenant Settings" },
];

export const MODULE_ACTIONS = ["read", "create", "update", "edit"] as const;
export type ModuleAction = (typeof MODULE_ACTIONS)[number];

export const ACTION_LABELS: Record<ModuleAction, string> = {
  read: "Read",
  create: "Create",
  update: "Update",
  edit: "Edit",
};

/** Extra permissions shown below the matrix (not part of the standard four). */
export const SPECIAL_PERMISSIONS: { resource: string; action: string; label: string }[] = [
  { resource: "org", action: "delete", label: "Organization — Delete nodes" },
  { resource: "org", action: "manage_types", label: "Organization — Manage level types" },
  { resource: "leave", action: "request", label: "Leave — Submit requests" },
  { resource: "approval", action: "action", label: "Approvals — Approve / reject" },
  { resource: "tenant", action: "settings", label: "Tenant — Settings" },
];

export function permissionKey(resource: string, action: string) {
  return `${resource}:${action}`;
}
