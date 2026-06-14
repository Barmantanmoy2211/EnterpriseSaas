"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Cpu, Plus } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { resourcesApi } from "@/lib/api/resources";
import { useAuthStore } from "@/stores/auth-store";

export default function ResourcesPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", resource_type: "equipment", capacity: 1, capacity_unit: "hours" });

  const { data: resources = [], isLoading } = useQuery({
    queryKey: ["resources"],
    queryFn: () => resourcesApi.list(accessToken!),
    enabled: !!accessToken,
  });

  const create = useMutation({
    mutationFn: () => resourcesApi.create(accessToken!, form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resources"] });
      setShowForm(false);
      setForm({ name: "", resource_type: "equipment", capacity: 1, capacity_unit: "hours" });
    },
  });

  return (
    <AppShell title="Resources">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Resource Management</h2>
            <p className="text-muted-foreground">{resources.length} resource(s)</p>
          </div>
          <Button onClick={() => setShowForm(!showForm)}><Plus className="mr-1 h-4 w-4" />Add resource</Button>
        </div>
        {showForm && (
          <Card>
            <CardHeader><CardTitle>New resource</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div><Label>Name</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
              <div><Label>Type</Label><Input value={form.resource_type} onChange={(e) => setForm({ ...form, resource_type: e.target.value })} /></div>
              <Button disabled={create.isPending} onClick={() => create.mutate()}>Create</Button>
            </CardContent>
          </Card>
        )}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {isLoading && <p className="text-muted-foreground">Loading...</p>}
          {resources.map((r) => (
            <Card key={r.id}>
              <CardHeader className="flex flex-row items-center gap-3 pb-2">
                <Cpu className="h-5 w-5 text-primary" />
                <CardTitle className="text-base">{r.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm capitalize">{r.resource_type}</p>
                <p className="text-xs text-muted-foreground">{r.capacity} {r.capacity_unit}</p>
                <Badge variant="secondary" className="mt-2">{r.status}</Badge>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
