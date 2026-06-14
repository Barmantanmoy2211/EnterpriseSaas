"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Briefcase, Plus, UserPlus } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { recruitmentApi } from "@/lib/api/recruitment";
import { useAuthStore } from "@/stores/auth-store";

export default function RecruitmentPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<"jobs" | "candidates" | "pipeline">("jobs");
  const [jobTitle, setJobTitle] = useState("");
  const [candidate, setCandidate] = useState({ first_name: "", last_name: "", email: "" });

  const { data: jobs = [] } = useQuery({
    queryKey: ["jobs"],
    queryFn: () => recruitmentApi.listJobs(accessToken!),
    enabled: !!accessToken,
  });

  const { data: candidates = [] } = useQuery({
    queryKey: ["candidates"],
    queryFn: () => recruitmentApi.listCandidates(accessToken!),
    enabled: !!accessToken,
  });

  const { data: applications = [] } = useQuery({
    queryKey: ["applications"],
    queryFn: () => recruitmentApi.listApplications(accessToken!),
    enabled: !!accessToken,
  });

  const createJob = useMutation({
    mutationFn: () => recruitmentApi.createJob(accessToken!, { title: jobTitle }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      setJobTitle("");
    },
  });

  const createCandidate = useMutation({
    mutationFn: () => recruitmentApi.createCandidate(accessToken!, candidate),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["candidates"] });
      setCandidate({ first_name: "", last_name: "", email: "" });
    },
  });

  const advanceApp = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      recruitmentApi.updateApplication(accessToken!, id, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applications"] }),
  });

  const stages = ["applied", "screening", "interview", "offer", "hired", "rejected"];

  return (
    <AppShell title="Recruitment">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold">Applicant Tracking System</h2>
          <p className="text-muted-foreground">Manage jobs, candidates, and hiring pipeline</p>
        </div>

        <div className="flex gap-2">
          {(["jobs", "candidates", "pipeline"] as const).map((t) => (
            <Button key={t} variant={tab === t ? "default" : "outline"} size="sm" onClick={() => setTab(t)}>
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </Button>
          ))}
        </div>

        {tab === "jobs" && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Briefcase className="h-5 w-5" />Open positions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input placeholder="Job title" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} />
                <Button onClick={() => createJob.mutate()} disabled={!jobTitle}>Post job</Button>
              </div>
              {jobs.map((job) => (
                <div key={job.id} className="flex items-center justify-between rounded-lg border p-3">
                  <div>
                    <p className="font-medium">{job.title}</p>
                    <p className="text-sm text-muted-foreground">{job.location || "Remote"}</p>
                  </div>
                  <Badge>{job.status}</Badge>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {tab === "candidates" && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><UserPlus className="h-5 w-5" />Candidates</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-3 sm:grid-cols-3">
                <div><Label>First name</Label><Input value={candidate.first_name} onChange={(e) => setCandidate({ ...candidate, first_name: e.target.value })} /></div>
                <div><Label>Last name</Label><Input value={candidate.last_name} onChange={(e) => setCandidate({ ...candidate, last_name: e.target.value })} /></div>
                <div><Label>Email</Label><Input value={candidate.email} onChange={(e) => setCandidate({ ...candidate, email: e.target.value })} /></div>
              </div>
              <Button onClick={() => createCandidate.mutate()}><Plus className="mr-1 h-4 w-4" />Add candidate</Button>
              {candidates.map((c) => (
                <div key={c.id} className="rounded-lg border p-3">
                  <p className="font-medium">{c.first_name} {c.last_name}</p>
                  <p className="text-sm text-muted-foreground">{c.email}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {tab === "pipeline" && (
          <Card>
            <CardHeader>
              <CardTitle>Application pipeline</CardTitle>
              <CardDescription>{applications.length} application(s)</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {applications.map((app) => {
                const job = jobs.find((j) => j.id === app.job_id);
                const cand = candidates.find((c) => c.id === app.candidate_id);
                const nextIdx = stages.indexOf(app.status) + 1;
                const nextStage = nextIdx < stages.length ? stages[nextIdx] : null;
                return (
                  <div key={app.id} className="flex items-center justify-between rounded-lg border p-3">
                    <div>
                      <p className="font-medium">{cand ? `${cand.first_name} ${cand.last_name}` : app.candidate_id}</p>
                      <p className="text-sm text-muted-foreground">{job?.title ?? "Unknown job"}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge>{app.status}</Badge>
                      {nextStage && nextStage !== "rejected" && (
                        <Button size="sm" variant="outline" onClick={() => advanceApp.mutate({ id: app.id, status: nextStage })}>
                          → {nextStage}
                        </Button>
                      )}
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
