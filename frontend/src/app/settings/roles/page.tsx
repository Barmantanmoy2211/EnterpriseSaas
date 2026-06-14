"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authApi } from "@/lib/api/auth";
import { permissionsApi } from "@/lib/api/permissions";
import { useAuthStore } from "@/stores/auth-store";

const ROLE_DESCRIPTIONS: Record<string, string> = {
  tenant_admin: "Full access — assigned automatically to whoever registers the workspace.",
  hr_manager: "Manage employees, recruitment, leave, attendance, and performance.",
  operations_manager: "Projects, tasks, calendar, documents, reports, and analytics.",
  enterprise_manager: "Inventory, finance, procurement, manufacturing, and logistics.",
  manager: "Read access plus approvals and leave management.",
  employee: "Self-service: leave requests, attendance, own tasks and calendar.",
  viewer: "Read-only access across all modules.",
};

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
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["role-assignments"] });
      setAssignUserId("");
      setAssignRoleId("");
    },
  });

  const deleteAssignment = useMutation({
    mutationFn: (id: string) => permissionsApi.deleteAssignment(accessToken!, id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["role-assignments"] }),
  });

  const togglePerm = (permId: string) => {
    setSelectedPerms((prev) =>
      prev.includes(permId) ? prev.filter((id) => id !== permId) : [...prev, permId],
    );
  };

  const userName = (userId: string) => {
    const u = users.find((x) => x.id === userId);
    if (!u) return userId.slice(-6);
    return u.first_name ? `${u.first_name} ${u.last_name}`.trim() : u.email;
  };

  const roleName = (roleId: string) => roles.find((r) => r.id === roleId)?.name ?? roleId.slice(-6);

  return (
    <AppShell title="Roles & Permissions">
      <div className="mx-auto max-w-5xl space-y-6">
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">How admin access works</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground space-y-2">
            <p>
              The person who <strong className="text-foreground">registers a new workspace</strong> is
              automatically assigned the <Badge variant="secondary">Tenant Administrator</Badge> role
              with full permissions.
            </p>
            <p>
              To give others access, assign them a role below (e.g. HR Manager, Employee, Viewer).
              Users need a role assignment to see modules in the sidebar.
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
                <p className="text-sm text-muted-foreground">
                  System roles are created when your workspace is registered
                </p>
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
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-4 sm:grid-cols-2">
                    <div>
                      <Label>Code</Label>
                      <Input value={code} onChange={(e) => setCode(e.target.value)} placeholder="custom_role" />
                    </div>
                    <div>
                      <Label>Name</Label>
                      <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Custom Role" />
                    </div>
                  </div>
                  <div>
                    <Label>Permissions</Label>
                    <div className="mt-2 max-h-48 overflow-y-auto grid gap-2 sm:grid-cols-2">
                      {permissions.map((perm) => (
                        <label
                          key={perm.id}
                          className="flex cursor-pointer items-center gap-2 rounded-md border p-2 text-sm"
                        >
                          <input
                            type="checkbox"
                            checked={selectedPerms.includes(perm.id)}
                            onChange={() => togglePerm(perm.id)}
                          />
                          <span>{perm.resource}:{perm.action}</span>
                        </label>
                      ))}
                    </div>
                  </div>
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
              <p className="text-sm text-muted-foreground">Map users to roles</p>
            </div>

            {isTenantAdmin && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Assign role to user</CardTitle>
                </CardHeader>
                <CardContent className="grid gap-4 sm:grid-cols-3">
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
                          {u.roles?.length ? ` (${u.roles.map((r) => r.name).join(", ")})` : ""}
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
                      <p className="text-sm text-muted-foreground">Role: {roleName(a.role_id)}</p>
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
