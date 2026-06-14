"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { BarChart3, Play } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { reportsApi, type ReportRun } from "@/lib/api/reports";
import { useAuthStore } from "@/stores/auth-store";

export default function ReportsPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const [lastRun, setLastRun] = useState<ReportRun | null>(null);

  const { data: reports = [], isLoading } = useQuery({
    queryKey: ["reports"],
    queryFn: () => reportsApi.list(accessToken!),
    enabled: !!accessToken,
  });

  const run = useMutation({
    mutationFn: (id: string) => reportsApi.run(accessToken!, id),
    onSuccess: (data) => setLastRun(data),
  });

  return (
    <AppShell title="Reports">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold">Reports</h2>
          <p className="text-muted-foreground">{reports.length} saved report(s)</p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {isLoading && <p className="text-muted-foreground">Loading...</p>}
          {reports.map((report) => (
            <Card key={report.id}>
              <CardHeader className="flex flex-row items-center gap-3 pb-2">
                <BarChart3 className="h-5 w-5 text-primary" />
                <div>
                  <CardTitle className="text-base">{report.name}</CardTitle>
                  <Badge variant="outline" className="mt-1">{report.entity_type}</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{report.description || "—"}</p>
                <Button
                  size="sm"
                  className="mt-3"
                  disabled={run.isPending}
                  onClick={() => run.mutate(report.id)}
                >
                  <Play className="mr-1 h-3 w-3" />
                  Run
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {lastRun && (
          <Card>
            <CardHeader>
              <CardTitle>Last run — {lastRun.row_count} row(s)</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="max-h-64 overflow-auto rounded bg-muted p-4 text-xs">
                {JSON.stringify(lastRun.result_preview, null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
