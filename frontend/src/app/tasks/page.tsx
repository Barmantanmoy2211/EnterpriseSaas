"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ListTodo, Plus } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { tasksApi } from "@/lib/api/tasks";
import { useAuthStore } from "@/stores/auth-store";

export default function TasksPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: "", description: "", priority: "medium", status: "todo" });

  const { data: tasks = [], isLoading } = useQuery({
    queryKey: ["tasks"],
    queryFn: () => tasksApi.list(accessToken!),
    enabled: !!accessToken,
  });

  const create = useMutation({
    mutationFn: () => tasksApi.create(accessToken!, form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      setShowForm(false);
      setForm({ title: "", description: "", priority: "medium", status: "todo" });
    },
  });

  const updateStatus = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      tasksApi.update(accessToken!, id, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tasks"] }),
  });

  return (
    <AppShell title="Tasks">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Task Board</h2>
            <p className="text-muted-foreground">{tasks.length} task(s)</p>
          </div>
          <Button onClick={() => setShowForm(!showForm)}>
            <Plus className="mr-1 h-4 w-4" />
            New task
          </Button>
        </div>

        {showForm && (
          <Card>
            <CardHeader><CardTitle>New task</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div><Label>Title</Label><Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /></div>
              <div><Label>Description</Label><Input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
              <Button disabled={create.isPending} onClick={() => create.mutate()}>Create</Button>
            </CardContent>
          </Card>
        )}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {isLoading && <p className="text-muted-foreground">Loading...</p>}
          {tasks.map((task) => (
            <Card key={task.id}>
              <CardHeader className="flex flex-row items-center gap-3 pb-2">
                <ListTodo className="h-5 w-5 text-primary" />
                <CardTitle className="text-base">{task.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground line-clamp-2">{task.description || "—"}</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  <Badge variant="secondary">{task.status}</Badge>
                  <Badge variant="outline">{task.priority}</Badge>
                </div>
                {task.status === "todo" && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="mt-3"
                    onClick={() => updateStatus.mutate({ id: task.id, status: "in_progress" })}
                  >
                    Start
                  </Button>
                )}
                {task.status === "in_progress" && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="mt-3"
                    onClick={() => updateStatus.mutate({ id: task.id, status: "done" })}
                  >
                    Complete
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
