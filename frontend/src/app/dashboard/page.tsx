"use client";

import { useQuery } from "@tanstack/react-query";
import { Building2, Shield, Users } from "lucide-react";

import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { organizationApi } from "@/lib/api/organization";
import { permissionsApi } from "@/lib/api/permissions";
import { tenantApi } from "@/lib/api/tenant";
import { useAuthStore } from "@/stores/auth-store";

export default function DashboardPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const user = useAuthStore((s) => s.user);

  const { data: tenant } = useQuery({
    queryKey: ["tenant"],
    queryFn: () => tenantApi.getMe(accessToken!),
    enabled: !!accessToken,
  });

  const { data: tree } = useQuery({
    queryKey: ["org-tree"],
    queryFn: () => organizationApi.getTree(accessToken!),
    enabled: !!accessToken,
  });

  const { data: roles } = useQuery({
    queryKey: ["roles"],
    queryFn: () => permissionsApi.listRoles(accessToken!),
    enabled: !!accessToken,
  });

  const countNodes = (nodes: typeof tree): number => {
    if (!nodes) return 0;
    return nodes.reduce((acc, n) => acc + 1 + countNodes(n.children), 0);
  };

  const stats = [
    {
      title: "Organization nodes",
      value: countNodes(tree),
      icon: Building2,
      description: "Across your hierarchy",
    },
    {
      title: "Roles defined",
      value: roles?.length ?? 0,
      icon: Shield,
      description: "Permission groups",
    },
    {
      title: "Workspace",
      value: tenant?.name ?? "—",
      icon: Users,
      description: tenant?.plan ?? "starter",
    },
  ];

  return (
    <AppShell title="Dashboard">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold">
            Welcome{user?.first_name ? `, ${user.first_name}` : ""}
          </h2>
          <p className="text-muted-foreground">
            Your enterprise platform is ready. Configure organization, roles, and modules from here.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <Card key={stat.title}>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {stat.title}
                  </CardTitle>
                  <Icon className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stat.value}</div>
                  <p className="text-xs text-muted-foreground">{stat.description}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Getting started</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>1. Configure organization node types and build your hierarchy</p>
            <p>2. Define roles and assign permissions to team members</p>
            <p>3. Customize tenant branding in settings</p>
            <p>4. Business modules (HR, Projects, Finance) plug in on top of this foundation</p>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
