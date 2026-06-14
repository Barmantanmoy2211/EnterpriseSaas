"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { tenantApi } from "@/lib/api/tenant";
import { useAuthStore } from "@/stores/auth-store";

export default function TenantSettingsPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();

  const { data: tenant } = useQuery({
    queryKey: ["tenant"],
    queryFn: () => tenantApi.getMe(accessToken!),
    enabled: !!accessToken,
  });

  const { data: settings } = useQuery({
    queryKey: ["tenant-settings"],
    queryFn: () => tenantApi.getSettings(accessToken!),
    enabled: !!accessToken,
  });

  const [name, setName] = useState("");
  const [primaryColor, setPrimaryColor] = useState("#2563eb");

  const updateTenant = useMutation({
    mutationFn: () => tenantApi.updateMe(accessToken!, { name: name || tenant?.name }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tenant"] }),
  });

  const updateSettings = useMutation({
    mutationFn: () =>
      tenantApi.updateSettings(accessToken!, {
        branding: { primary_color: primaryColor },
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tenant-settings"] }),
  });

  return (
    <AppShell title="Tenant Settings">
      <div className="mx-auto max-w-2xl space-y-6">
        <div>
          <h2 className="text-2xl font-bold">Workspace settings</h2>
          <p className="text-muted-foreground">Customize your organization workspace</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>General</CardTitle>
            <CardDescription>Workspace name and identifier</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Workspace name</Label>
              <Input
                className="mt-2"
                defaultValue={tenant?.name}
                onChange={(e) => setName(e.target.value)}
                placeholder={tenant?.name}
              />
            </div>
            <div>
              <Label>Slug</Label>
              <Input className="mt-2" value={tenant?.slug ?? ""} disabled />
            </div>
            <div>
              <Label>Plan</Label>
              <Input className="mt-2" value={tenant?.plan ?? ""} disabled />
            </div>
            <Button onClick={() => updateTenant.mutate()} disabled={updateTenant.isPending}>
              Save general settings
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Branding</CardTitle>
            <CardDescription>Customize appearance for your workspace</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Primary color</Label>
              <div className="mt-2 flex items-center gap-3">
                <input
                  type="color"
                  value={primaryColor}
                  onChange={(e) => setPrimaryColor(e.target.value)}
                  className="h-10 w-14 cursor-pointer rounded border"
                />
                <Input
                  value={primaryColor}
                  onChange={(e) => setPrimaryColor(e.target.value)}
                  className="max-w-[140px]"
                />
                <div
                  className="h-10 flex-1 rounded-lg"
                  style={{ backgroundColor: settings?.branding?.primary_color ?? primaryColor }}
                />
              </div>
            </div>
            <Button onClick={() => updateSettings.mutate()} disabled={updateSettings.isPending}>
              Save branding
            </Button>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
