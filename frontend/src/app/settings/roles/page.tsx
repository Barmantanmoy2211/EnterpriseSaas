"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { permissionsApi } from "@/lib/api/permissions";
import { useAuthStore } from "@/stores/auth-store";

export default function RolesSettingsPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [selectedPerms, setSelectedPerms] = useState<string[]>([]);

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

  const createRole = useMutation({
    mutationFn: () =>
      permissionsApi.createRole(accessToken!, {
        code,
        name,
        permission_ids: selectedPerms,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roles"] });
      setShowForm(false);
      setCode("");
      setName("");
      setSelectedPerms([]);
    },
  });

  const togglePerm = (permId: string) => {
    setSelectedPerms((prev) =>
      prev.includes(permId) ? prev.filter((id) => id !== permId) : [...prev, permId],
    );
  };

  return (
    <AppShell title="Roles & Permissions">
      <div className="mx-auto max-w-4xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Roles</h2>
            <p className="text-muted-foreground">Manage access control for your workspace</p>
          </div>
          <Button onClick={() => setShowForm(!showForm)}>
            {showForm ? "Cancel" : "Create role"}
          </Button>
        </div>

        {showForm && (
          <Card>
            <CardHeader>
              <CardTitle>New role</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Code</Label>
                  <Input value={code} onChange={(e) => setCode(e.target.value)} placeholder="hr_manager" />
                </div>
                <div>
                  <Label>Name</Label>
                  <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="HR Manager" />
                </div>
              </div>
              <div>
                <Label>Permissions</Label>
                <div className="mt-2 grid gap-2 sm:grid-cols-2">
                  {permissions.map((perm) => (
                    <label
                      key={perm.id}
                      className="flex cursor-pointer items-center gap-2 rounded-lg border p-2 text-sm"
                    >
                      <input
                        type="checkbox"
                        checked={selectedPerms.includes(perm.id)}
                        onChange={() => togglePerm(perm.id)}
                      />
                      <span>
                        {perm.resource}:{perm.action}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
              <Button
                disabled={!code || !name || createRole.isPending}
                onClick={() => createRole.mutate()}
              >
                Create role
              </Button>
            </CardContent>
          </Card>
        )}

        <div className="grid gap-4">
          {roles.map((role) => (
            <Card key={role.id}>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <CardTitle className="text-lg">{role.name}</CardTitle>
                  <Badge variant="outline">{role.code}</Badge>
                  {role.is_system && <Badge>System</Badge>}
                </div>
                <CardDescription>{role.description || "No description"}</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {role.permission_ids.length} permission(s) assigned
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Available permissions</CardTitle>
            <CardDescription>System-defined permissions for Phase 1</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {permissions.map((perm) => (
                <Badge key={perm.id} variant="secondary">
                  {perm.resource}:{perm.action}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
