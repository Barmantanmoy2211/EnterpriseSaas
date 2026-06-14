"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, X } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { approvalsApi } from "@/lib/api/approvals";
import { useAuthStore } from "@/stores/auth-store";

export default function ApprovalsPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();
  const [comments, setComments] = useState<Record<string, string>>({});

  const { data: pending = [] } = useQuery({
    queryKey: ["approvals-pending"],
    queryFn: () => approvalsApi.listPending(accessToken!),
    enabled: !!accessToken,
  });

  const { data: mine = [] } = useQuery({
    queryKey: ["approvals-mine"],
    queryFn: () => approvalsApi.listMine(accessToken!),
    enabled: !!accessToken,
  });

  const approve = useMutation({
    mutationFn: (id: string) => approvalsApi.approve(accessToken!, id, comments[id] || ""),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["approvals-pending"] });
      queryClient.invalidateQueries({ queryKey: ["approvals-mine"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const reject = useMutation({
    mutationFn: (id: string) => approvalsApi.reject(accessToken!, id, comments[id] || ""),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["approvals-pending"] });
      queryClient.invalidateQueries({ queryKey: ["approvals-mine"] });
    },
  });

  return (
    <AppShell title="Approvals">
      <div className="mx-auto max-w-4xl space-y-6">
        <div>
          <h2 className="text-2xl font-bold">Approval Inbox</h2>
          <p className="text-muted-foreground">Hierarchy-aware approvals linked to workflows</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Pending your action</CardTitle>
            <CardDescription>{pending.length} request(s)</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {pending.length === 0 && (
              <p className="text-sm text-muted-foreground">No pending approvals</p>
            )}
            {pending.map((a) => (
              <div key={a.id} className="rounded-lg border p-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="font-medium">{a.title}</p>
                    <p className="text-sm text-muted-foreground">{a.description}</p>
                    <Badge variant="secondary" className="mt-2">
                      {a.status}
                    </Badge>
                  </div>
                </div>
                <Input
                  className="mt-3"
                  placeholder="Comments (optional)"
                  value={comments[a.id] || ""}
                  onChange={(e) => setComments((c) => ({ ...c, [a.id]: e.target.value }))}
                />
                <div className="mt-3 flex gap-2">
                  <Button size="sm" onClick={() => approve.mutate(a.id)} disabled={approve.isPending}>
                    <Check className="mr-1 h-4 w-4" />
                    Approve
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => reject.mutate(a.id)}
                    disabled={reject.isPending}
                  >
                    <X className="mr-1 h-4 w-4" />
                    Reject
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>My requests</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {mine.map((a) => (
              <div key={a.id} className="flex items-center justify-between rounded-lg border p-3">
                <div>
                  <p className="font-medium">{a.title}</p>
                  <p className="text-xs text-muted-foreground">{a.created_at}</p>
                </div>
                <Badge variant={a.status === "approved" ? "default" : "secondary"}>{a.status}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
