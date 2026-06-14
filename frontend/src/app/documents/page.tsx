"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FileStack, Plus } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { documentsApi } from "@/lib/api/documents";
import { useAuthStore } from "@/stores/auth-store";

export default function DocumentsPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: "", description: "", file_url: "", folder_path: "/" });

  const { data: documents = [], isLoading } = useQuery({
    queryKey: ["documents"],
    queryFn: () => documentsApi.list(accessToken!),
    enabled: !!accessToken,
  });

  const create = useMutation({
    mutationFn: () => documentsApi.create(accessToken!, form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      setShowForm(false);
      setForm({ title: "", description: "", file_url: "", folder_path: "/" });
    },
  });

  return (
    <AppShell title="Documents">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Document Library</h2>
            <p className="text-muted-foreground">{documents.length} document(s)</p>
          </div>
          <Button onClick={() => setShowForm(!showForm)}>
            <Plus className="mr-1 h-4 w-4" />
            Add document
          </Button>
        </div>

        {showForm && (
          <Card>
            <CardHeader><CardTitle>New document</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div><Label>Title</Label><Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /></div>
              <div><Label>File URL</Label><Input placeholder="https://..." value={form.file_url} onChange={(e) => setForm({ ...form, file_url: e.target.value })} /></div>
              <div className="sm:col-span-2"><Label>Description</Label><Input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
              <Button disabled={create.isPending} onClick={() => create.mutate()}>Create</Button>
            </CardContent>
          </Card>
        )}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {isLoading && <p className="text-muted-foreground">Loading...</p>}
          {documents.map((doc) => (
            <Card key={doc.id}>
              <CardHeader className="flex flex-row items-center gap-3 pb-2">
                <FileStack className="h-5 w-5 text-primary" />
                <CardTitle className="text-base">{doc.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{doc.description || "—"}</p>
                <p className="mt-1 text-xs text-muted-foreground">{doc.folder_path} · v{doc.version}</p>
                {doc.file_url && (
                  <a href={doc.file_url} target="_blank" rel="noreferrer" className="mt-2 inline-block text-sm text-primary hover:underline">
                    Open file
                  </a>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
