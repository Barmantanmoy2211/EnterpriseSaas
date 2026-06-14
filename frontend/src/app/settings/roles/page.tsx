"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { ModulePermissionMatrix } from "@/components/permissions/module-permission-matrix";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authApi } from "@/lib/api/auth";
import { organizationApi, type OrgNode } from "@/lib/api/organization";
import { permissionsApi } from "@/lib/api/permissions";
import { useAuthStore } from "@/stores/auth-store";

const ROLE_DESCRIPTIONS: Record<string, string> = {
  tenant_admin: "Full access — assigned automatically to whoever registers the workspace.",
  hierarchy_admin:
    "Assign to a hierarchy node — full module access for that node and everything below it.",
  hr_manager: "Manage employees, recruitment, leave, attendance, and performance.",
  operations_manager: "Projects, tasks, calendar, documents, reports, and analytics.",
  enterprise_manager: "Inventory, finance, procurement, manufacturing, and logistics.",
  manager: "Read access plus approvals and leave management.",
  employee: "Self-service: leave requests, attendance, own tasks and calendar.",
  viewer: "Read-only access across all modules.",
};

function flattenOrgNodes(tree: OrgNode[], depth = 0): { id: string; label: string }[] {
  const items: { id: string; label: string }[] = [];
  for (const node of tree) {
    items.push({
      id: node.id,
      label: `${"—".repeat(depth)}${depth > 0 ? " " : ""}${node.name}`,
    });
    items.push(...flattenOrgNodes(node.children, depth + 1));
  }
  return items;
}

export default function RolesSettingsPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const isTenantAdmin = useAuthStore((s) => s.isTenantAdmin);
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<"roles" | "assignments">("roles");
  const [showForm, setShowForm] = useState(false);
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [selectedPerms, setSelectedPerms] = useState<string[]>([]);
  const [assignUserId, setAssignUserId] = useState("");
  const [assignRoleId, setAssignRoleId] = useState("");
  const [assignScopeNodeId, setAssignScopeNodeId] = useState("");

  const { data: roles = [] } = useQuery({
    queryKey: ["roles"],
    queryFn: () => permissionsApi.listRoles(accessToken!),
    enabled: !!accessToken,
  });

  const { data: permissions = [] } = useQuery({
    queryKey: ["permissions"],
    queryFn: () => permissionsApi.listPermissions(accessToken!),
    enabled: !!accessToken,
  });

  const { data: assignments = [] } = useQuery({
    queryKey: ["role-assignments"],
    queryFn: () => permissionsApi.listAssignments(accessToken!),
    enabled: !!accessToken,
  });

  const { data: users = [] } = useQuery({
    queryKey: ["tenant-users"],
    queryFn: () => authApi.listUsers(accessToken!),
    enabled: !!accessToken && isTenantAdmin,
  });

  const { data: orgTree = [] } = useQuery({
    queryKey: ["org-tree"],
    queryFn: () => organizationApi.getTree(accessToken!),
    enabled: !!accessToken && isTenantAdmin,
  });

  const orgNodeOptions = useMemo(() => flattenOrgNodes(orgTree), [orgTree]);

  const createRole = useMutation({
    mutationFn: () =>
      permissionsApi.createRole(accessToken!, { code, name, permission_ids: selectedPerms }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roles"] });
      setShowForm(false);
      setCode("");
      setName("");
      setSelectedPerms([]);
    },
  });

  const createAssignment = useMutation({
    mutationFn: () =>
      permissionsApi.createAssignment(accessToken!, {
        user_id: assignUserId,
        role_id: assignRoleId,
        scope_node_id: assignScopeNodeId || null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["role-assignments"] });
      setAssignUserId("");
      setAssignRoleId("");
      setAssignScopeNodeId("");
    },
  });

  const deleteAssignment = useMutation({
    mutationFn: (id: string) => permissionsApi.deleteAssignment(accessToken!, id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["role-assignments"] }),
  });

  const userName = (userId: string) => {
    const u = users.find((x) => x.id === userId);
    if (!u) return userId.slice(-6);
    return u.first_name ? `${u.first_name} ${u.last_name}`.trim() : u.email;
  };

  const roleName = (roleId: string) => roles.find((r) => r.id === roleId)?.name ?? roleId.slice(-6);

  const scopeLabel = (scopeId: string | null) => {
    if (!scopeId) return "All organization (global)";
    const node = orgNodeOptions.find((o) => o.id === scopeId);
    return node?.label.trim() ?? scopeId.slice(-6);
  };

  return (
    <AppShell title="Roles & Permissions">
      <div className="mx-auto max-w-5xl space-y-6">
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Hierarchy-scoped access</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>
              Use the <Badge variant="secondary">Hierarchy Admin</Badge> role and pick a{" "}
              <strong className="text-foreground">hierarchy scope</strong> when assigning — that user
              gets full access to all modules within that node and its children.
            </p>
            <p>
              Permissions use a module matrix: <strong className="text-foreground">Read</strong>,{" "}
              <strong className="text-foreground">Create</strong>,{" "}
              <strong className="text-foreground">Update</strong>, and{" "}
              <strong className="text-foreground">Edit</strong> per module.
            </p>
          </CardContent>
        </Card>

        <div className="flex gap-2 border-b pb-2">
          <Button variant={tab === "roles" ? "default" : "ghost"} size="sm" onClick={() => setTab("roles")}>
            Role templates
          </Button>
          <Button
            variant={tab === "assignments" ? "default" : "ghost"}
            size="sm"
            onClick={() => setTab("assignments")}
          >
            User assignments
          </Button>
        </div>

        {tab === "roles" && (
          <>
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold">Roles</h2>
                <p className="text-sm text-muted-foreground">Module permissions per role</p>
              </div>
              {isTenantAdmin && (
                <Button onClick={() => setShowForm(!showForm)}>
                  {showForm ? "Cancel" : "Custom role"}
                </Button>
              )}
            </div>

            {showForm && (
              <Card>
                <CardHeader>
                  <CardTitle>Custom role</CardTitle>
                  <CardDescription>Pick module permissions using the matrix below</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-4 sm:grid-cols-2">
                    <div>
                      <Label>Code</Label>
                      <Input value={code} onChange={(e) => setCode(e.target.value)} placeholder="region_admin" />
                    </div>
                    <div>
                      <Label>Name</Label>
                      <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Region Admin" />
                    </div>
                  </div>
                  <ModulePermissionMatrix
                    permissions={permissions}
                    selectedIds={selectedPerms}
                    onChange={setSelectedPerms}
                  />
                  <Button disabled={!code || !name || createRole.isPending} onClick={() => createRole.mutate()}>
                    Create role
                  </Button>
                </CardContent>
              </Card>
            )}

            <div className="grid gap-4 sm:grid-cols-2">
              {roles.map((role) => (
                <Card key={role.id}>
                  <CardHeader className="pb-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <CardTitle className="text-base">{role.name}</CardTitle>
                      <Badge variant="outline" className="text-xs">{role.code}</Badge>
                      {role.is_system && <Badge className="text-xs">System</Badge>}
                    </div>
                    <CardDescription className="text-xs">
                      {ROLE_DESCRIPTIONS[role.code] || role.description || "No description"}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-xs text-muted-foreground">
                      {role.permission_ids.length} permission(s)
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </>
        )}

        {tab === "assignments" && (
          <>
            <div>
              <h2 className="text-xl font-bold">User assignments</h2>
              <p className="text-sm text-muted-foreground">
                Map users to roles and hierarchy scope (layer admin)
              </p>
            </div>

            {isTenantAdmin && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Assign role to user</CardTitle>
                </CardHeader>
                <CardContent className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  <div>
                    <Label>User</Label>
                    <select
                      className="mt-1 flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
                      value={assignUserId}
                      onChange={(e) => setAssignUserId(e.target.value)}
                    >
                      <option value="">Select user</option>
                      {users.map((u) => (
                        <option key={u.id} value={u.id}>
                          {u.email}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <Label>Role</Label>
                    <select
                      className="mt-1 flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
                      value={assignRoleId}
                      onChange={(e) => setAssignRoleId(e.target.value)}
                    >
                      <option value="">Select role</option>
                      {roles.map((r) => (
                        <option key={r.id} value={r.id}>
                          {r.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <Label>Hierarchy scope</Label>
                    <select
                      className="mt-1 flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
                      value={assignScopeNodeId}
                      onChange={(e) => setAssignScopeNodeId(e.target.value)}
                    >
                      <option value="">All organization (global)</option>
                      {orgNodeOptions.map((o) => (
                        <option key={o.id} value={o.id}>
                          {o.label}
                        </option>
                      ))}
                    </select>
                    <p className="mt-1 text-xs text-muted-foreground">
                      Required for Hierarchy Admin — limits access to this node and below.
                    </p>
                  </div>
                  <div className="flex items-end">
                    <Button
                      className="w-full"
                      disabled={!assignUserId || !assignRoleId || createAssignment.isPending}
                      onClick={() => createAssignment.mutate()}
                    >
                      Assign
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            <div className="space-y-2">
              {assignments.length === 0 && (
                <p className="text-sm text-muted-foreground">No assignments yet.</p>
              )}
              {assignments.map((a) => (
                <Card key={a.id}>
                  <CardContent className="flex items-center justify-between py-4">
                    <div>
                      <p className="font-medium">{userName(a.user_id)}</p>
                      <p className="text-sm text-muted-foreground">
                        Role: {roleName(a.role_id)}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Scope: {scopeLabel(a.scope_node_id)}
                      </p>
                    </div>
                    {isTenantAdmin && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-destructive"
                        onClick={() => deleteAssignment.mutate(a.id)}
                      >
                        Remove
                      </Button>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
