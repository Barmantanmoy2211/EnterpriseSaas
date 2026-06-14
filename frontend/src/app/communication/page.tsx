"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { MessageSquare, Plus } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { communicationApi } from "@/lib/api/communication";
import { useAuthStore } from "@/stores/auth-store";

export default function CommunicationPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ subject: "", body: "", message_type: "announcement", channel: "general" });

  const { data: messages = [], isLoading } = useQuery({
    queryKey: ["communication"],
    queryFn: () => communicationApi.list(accessToken!),
    enabled: !!accessToken,
  });

  const create = useMutation({
    mutationFn: () => communicationApi.create(accessToken!, form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["communication"] });
      setShowForm(false);
      setForm({ subject: "", body: "", message_type: "announcement", channel: "general" });
    },
  });

  return (
    <AppShell title="Communication">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Communication Hub</h2>
            <p className="text-muted-foreground">{messages.length} message(s)</p>
          </div>
          <Button onClick={() => setShowForm(!showForm)}>
            <Plus className="mr-1 h-4 w-4" />
            New announcement
          </Button>
        </div>

        {showForm && (
          <Card>
            <CardHeader><CardTitle>New announcement</CardTitle></CardHeader>
            <CardContent className="grid gap-4">
              <div><Label>Subject</Label><Input value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} /></div>
              <div><Label>Body</Label><Input value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} /></div>
              <Button disabled={create.isPending} onClick={() => create.mutate()}>Post</Button>
            </CardContent>
          </Card>
        )}

        <div className="space-y-3">
          {isLoading && <p className="text-muted-foreground">Loading...</p>}
          {messages.map((msg) => (
            <Card key={msg.id}>
              <CardHeader className="flex flex-row items-start gap-3 pb-2">
                <MessageSquare className="mt-1 h-5 w-5 text-primary" />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <CardTitle className="text-base">{msg.subject}</CardTitle>
                    {msg.is_pinned && <Badge variant="secondary">Pinned</Badge>}
                  </div>
                  <p className="text-xs text-muted-foreground">{new Date(msg.created_at).toLocaleString()}</p>
                </div>
              </CardHeader>
              <CardContent><p className="text-sm">{msg.body}</p></CardContent>
            </Card>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
