"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { workflowsApi } from "@/lib/api/workflows";
import { useAuthStore } from "@/stores/auth-store";

export default function WorkflowsPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [entityType, setEntityType] = useState("generic_request");

  const { data: definitions = [] } = useQuery({
    queryKey: ["workflow-definitions"],
    queryFn: () => workflowsApi.listDefinitions(accessToken!),
    enabled: !!accessToken,
  });

  const { data: instances = [] } = useQuery({
    queryKey: ["workflow-instances"],
    queryFn: () => workflowsApi.listInstances(accessToken!),
    enabled: !!accessToken,
  });

  const createDef = useMutation({
    mutationFn: () =>
      workflowsApi.createDefinition(accessToken!, {
        code,
        name,
        entity_type: entityType,
        steps: [
          {
            id: "approval_1",
            name: "Manager Approval",
            type: "approval",
            config: {
              title: "Approval required",
              approver_role_id: null,
              fallback_approver_id: useAuthStore.getState().user?.id,
            },
          },
          {
            id: "notify_1",
            name: "Notify requester",
            type: "notification",
            config: { title: "Request completed", body: "Your workflow has completed" },
          },
        ],
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflow-definitions"] });
      setShowForm(false);
    },
  });

  const startInstance = useMutation({
    mutationFn: (definitionCode: string) =>
      workflowsApi.startInstance(accessToken!, {
        definition_code: definitionCode,
        entity_type: entityType,
        entity_id: `req-${Date.now()}`,
        context: { entity_type: entityType },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflow-instances"] });
      queryClient.invalidateQueries({ queryKey: ["approvals-pending"] });
    },
  });

  return (
    <AppShell title="Workflows">
      <div className="mx-auto max-w-4xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Workflow Engine</h2>
            <p className="text-muted-foreground">Reusable workflows across all business modules</p>
          </div>
          <Button onClick={() => setShowForm(!showForm)}>
            <Plus className="mr-1 h-4 w-4" />
            New definition
          </Button>
        </div>

        {showForm && (
          <Card>
            <CardHeader>
              <CardTitle>Create workflow definition</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label>Code</Label>
                <Input value={code} onChange={(e) => setCode(e.target.value)} placeholder="leave_approval" />
              </div>
              <div>
                <Label>Name</Label>
                <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Leave Approval" />
              </div>
              <div className="sm:col-span-2">
                <Label>Entity type</Label>
                <Input value={entityType} onChange={(e) => setEntityType(e.target.value)} />
              </div>
              <Button
                disabled={!code || !name || createDef.isPending}
                onClick={() => createDef.mutate()}
              >
                Create
              </Button>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Definitions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {definitions.map((d) => (
              <div key={d.id} className="flex items-center justify-between rounded-lg border p-4">
                <div>
                  <p className="font-medium">{d.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {d.code} · {d.steps.length} step(s)
                  </p>
                </div>
                <Button size="sm" variant="outline" onClick={() => startInstance.mutate(d.code)}>
                  Start instance
                </Button>
              </div>
            ))}
            {definitions.length === 0 && (
              <p className="text-sm text-muted-foreground">No workflow definitions yet</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Active instances</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {instances.map((i) => (
              <div key={i.id} className="flex items-center justify-between rounded-lg border p-3">
                <div>
                  <p className="font-medium">
                    {i.entity_type} / {i.entity_id}
                  </p>
                  <p className="text-xs text-muted-foreground">Step: {i.current_step_id ?? "—"}</p>
                </div>
                <Badge>{i.status}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
