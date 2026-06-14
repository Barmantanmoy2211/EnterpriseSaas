"use client";

import { useQuery } from "@tanstack/react-query";
import { LineChart, Users, FolderKanban, ListTodo, UserPlus, CheckSquare } from "lucide-react";

import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { analyticsApi } from "@/lib/api/analytics";
import { useAuthStore } from "@/stores/auth-store";

const statCards = [
  { key: "employees", label: "Employees", icon: Users },
  { key: "projects", label: "Projects", icon: FolderKanban },
  { key: "tasks", label: "Tasks", icon: ListTodo },
  { key: "pending_approvals", label: "Pending Approvals", icon: CheckSquare },
] as const;

export default function AnalyticsPage() {
  const accessToken = useAuthStore((s) => s.accessToken);

  const { data: overview, isLoading } = useQuery({
    queryKey: ["analytics"],
    queryFn: () => analyticsApi.overview(accessToken!),
    enabled: !!accessToken,
  });

  return (
    <AppShell title="Analytics">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold">Analytics Dashboard</h2>
          <p className="text-muted-foreground">Tenant-wide operational metrics</p>
        </div>

        {isLoading && <p className="text-muted-foreground">Loading...</p>}

        {overview && (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {statCards.map(({ key, label, icon: Icon }) => (
                <Card key={key}>
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-medium">{label}</CardTitle>
                    <Icon className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <p className="text-3xl font-bold">{overview.totals[key] ?? 0}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              <Card>
                <CardHeader className="flex flex-row items-center gap-2">
                  <LineChart className="h-5 w-5" />
                  <CardTitle>Employees by status</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-1 text-sm">
                    {Object.entries(overview.employees).map(([status, count]) => (
                      <li key={status} className="flex justify-between">
                        <span className="capitalize">{status}</span>
                        <span className="font-medium">{count}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center gap-2">
                  <UserPlus className="h-5 w-5" />
                  <CardTitle>Recruitment</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-1 text-sm">
                    <li className="flex justify-between">
                      <span>Job postings</span>
                      <span className="font-medium">{overview.recruitment.jobs ?? 0}</span>
                    </li>
                    <li className="flex justify-between">
                      <span>Applications</span>
                      <span className="font-medium">{overview.recruitment.applications ?? 0}</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Tasks by status</CardTitle></CardHeader>
                <CardContent>
                  <ul className="space-y-1 text-sm">
                    {Object.entries(overview.tasks).map(([status, count]) => (
                      <li key={status} className="flex justify-between">
                        <span className="capitalize">{status.replace("_", " ")}</span>
                        <span className="font-medium">{count}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Projects by status</CardTitle></CardHeader>
                <CardContent>
                  <ul className="space-y-1 text-sm">
                    {Object.entries(overview.projects).map(([status, count]) => (
                      <li key={status} className="flex justify-between">
                        <span className="capitalize">{status}</span>
                        <span className="font-medium">{count}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
