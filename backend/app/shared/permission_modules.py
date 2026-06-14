"""Module definitions for standardized RBAC (read / create / update / edit)."""

# (resource_code, display_label)
PERMISSION_MODULES: list[tuple[str, str]] = [
    ("org", "Organization"),
    ("employee", "Employees"),
    ("recruitment", "Recruitment"),
    ("leave", "Leave"),
    ("attendance", "Attendance"),
    ("performance", "Performance"),
    ("training", "Training"),
    ("onboarding", "Onboarding"),
    ("exit", "Exit & Offboarding"),
    ("project", "Projects"),
    ("task", "Tasks"),
    ("calendar", "Calendar"),
    ("document", "Documents"),
    ("communication", "Communication"),
    ("report", "Reports"),
    ("analytics", "Analytics"),
    ("inventory", "Inventory"),
    ("resource", "Resources"),
    ("finance", "Finance"),
    ("procurement", "Procurement"),
    ("manufacturing", "Manufacturing"),
    ("logistics", "Logistics"),
    ("approval", "Approvals"),
    ("workflow", "Workflows"),
    ("audit", "Audit Log"),
    ("notification", "Notifications"),
    ("search", "Search"),
    ("user", "Users"),
    ("role", "Roles"),
    ("tenant", "Tenant Settings"),
]

STANDARD_ACTIONS = ("read", "create", "update", "edit")

# Extra permissions beyond the standard four per module
SPECIAL_PERMISSIONS: list[tuple[str, str, str]] = [
    ("org", "delete", "Delete organization nodes"),
    ("org", "manage_types", "Configure hierarchy level types"),
    ("leave", "request", "Submit leave requests"),
    ("approval", "action", "Approve or reject requests"),
    ("tenant", "settings", "Manage tenant settings"),
]
