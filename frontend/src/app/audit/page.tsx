"use client";

import { useQuery } from "@tanstack/react-query";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { auditApi } from "@/lib/api/audit";
import { useAuthStore } from "@/stores/auth-store";

export default function AuditPage() {
  const accessToken = useAuthStore((s) => s.accessToken);

  const { data, isLoading } = useQuery({
    queryKey: ["audit-logs"],
    queryFn: () => auditApi.list(accessToken!, { limit: 100 }),
    enabled: !!accessToken,
  });

  return (
    <AppShell title="Audit Log">
      <div className="mx-auto max-w-5xl space-y-6">
        <div>
          <h2 className="text-2xl font-bold">Audit Trail</h2>
          <p className="text-muted-foreground">Immutable log of platform actions</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Recent events ({data?.total ?? 0})</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading && <p className="text-sm text-muted-foreground">Loading...</p>}
            <div className="space-y-2">
              {data?.items.map((log) => (
                <div
                  key={log.id}
                  className="flex flex-wrap items-center gap-2 rounded-lg border p-3 text-sm"
                >
                  <Badge variant="outline">{log.action}</Badge>
                  <span className="text-muted-foreground">{log.resource_type}</span>
                  {log.resource_id && (
                    <span className="font-mono text-xs">{log.resource_id.slice(0, 8)}...</span>
                  )}
                  <span className="ml-auto text-xs text-muted-foreground">
                    {new Date(log.created_at).toLocaleString()}
                  </span>
                </div>
              ))}
              {data?.items.length === 0 && !isLoading && (
                <p className="text-sm text-muted-foreground">No audit events yet</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
