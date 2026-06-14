"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CalendarDays, Plus } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { calendarApi } from "@/lib/api/calendar";
import { useAuthStore } from "@/stores/auth-store";

export default function CalendarPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: "", start_at: "", end_at: "", location: "" });

  const { data: events = [], isLoading } = useQuery({
    queryKey: ["calendar"],
    queryFn: () => calendarApi.list(accessToken!),
    enabled: !!accessToken,
  });

  const create = useMutation({
    mutationFn: () =>
      calendarApi.create(accessToken!, {
        ...form,
        start_at: new Date(form.start_at).toISOString(),
        end_at: new Date(form.end_at).toISOString(),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["calendar"] });
      setShowForm(false);
      setForm({ title: "", start_at: "", end_at: "", location: "" });
    },
  });

  return (
    <AppShell title="Calendar">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Calendar</h2>
            <p className="text-muted-foreground">{events.length} event(s)</p>
          </div>
          <Button onClick={() => setShowForm(!showForm)}>
            <Plus className="mr-1 h-4 w-4" />
            New event
          </Button>
        </div>

        {showForm && (
          <Card>
            <CardHeader><CardTitle>New event</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div><Label>Title</Label><Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /></div>
              <div><Label>Location</Label><Input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} /></div>
              <div><Label>Start</Label><Input type="datetime-local" value={form.start_at} onChange={(e) => setForm({ ...form, start_at: e.target.value })} /></div>
              <div><Label>End</Label><Input type="datetime-local" value={form.end_at} onChange={(e) => setForm({ ...form, end_at: e.target.value })} /></div>
              <Button disabled={create.isPending} onClick={() => create.mutate()}>Create</Button>
            </CardContent>
          </Card>
        )}

        <div className="space-y-3">
          {isLoading && <p className="text-muted-foreground">Loading...</p>}
          {events.map((event) => (
            <Card key={event.id}>
              <CardHeader className="flex flex-row items-center gap-3 pb-2">
                <CalendarDays className="h-5 w-5 text-primary" />
                <div>
                  <CardTitle className="text-base">{event.title}</CardTitle>
                  <p className="text-xs text-muted-foreground">
                    {new Date(event.start_at).toLocaleString()} — {new Date(event.end_at).toLocaleString()}
                  </p>
                </div>
              </CardHeader>
              {event.location && (
                <CardContent><p className="text-sm text-muted-foreground">{event.location}</p></CardContent>
              )}
            </Card>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
