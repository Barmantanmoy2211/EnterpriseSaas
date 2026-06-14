"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Star, Target } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { employeesApi } from "@/lib/api/employees";
import { performanceApi } from "@/lib/api/performance";
import { useAuthStore } from "@/stores/auth-store";

export default function PerformancePage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();
  const [reviewForm, setReviewForm] = useState({ employee_id: "", period: "", rating: "3", feedback: "" });
  const [goalForm, setGoalForm] = useState({ employee_id: "", title: "" });

  const { data: employees = [] } = useQuery({
    queryKey: ["employees"],
    queryFn: () => employeesApi.list(accessToken!),
    enabled: !!accessToken,
  });

  const { data: reviews = [] } = useQuery({
    queryKey: ["reviews"],
    queryFn: () => performanceApi.listReviews(accessToken!),
    enabled: !!accessToken,
  });

  const { data: goals = [] } = useQuery({
    queryKey: ["goals"],
    queryFn: () => performanceApi.listGoals(accessToken!),
    enabled: !!accessToken,
  });

  const { data: courses = [] } = useQuery({
    queryKey: ["courses"],
    queryFn: () => performanceApi.listCourses(accessToken!),
    enabled: !!accessToken,
  });

  const createReview = useMutation({
    mutationFn: () =>
      performanceApi.createReview(accessToken!, {
        ...reviewForm,
        rating: parseInt(reviewForm.rating, 10),
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["reviews"] }),
  });

  const createGoal = useMutation({
    mutationFn: () => performanceApi.createGoal(accessToken!, goalForm),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["goals"] }),
  });

  return (
    <AppShell title="Performance">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold">Performance & Training</h2>
          <p className="text-muted-foreground">Reviews, goals, and training courses</p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2"><Star className="h-5 w-5" />Reviews</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <Label>Employee</Label>
                  <select className="mt-1 flex h-10 w-full rounded-lg border px-3 text-sm" value={reviewForm.employee_id} onChange={(e) => setReviewForm({ ...reviewForm, employee_id: e.target.value })}>
                    <option value="">Select...</option>
                    {employees.map((e) => <option key={e.id} value={e.id}>{e.first_name} {e.last_name}</option>)}
                  </select>
                </div>
                <div><Label>Period</Label><Input placeholder="Q1 2026" value={reviewForm.period} onChange={(e) => setReviewForm({ ...reviewForm, period: e.target.value })} /></div>
                <div><Label>Rating (1-5)</Label><Input type="number" min="1" max="5" value={reviewForm.rating} onChange={(e) => setReviewForm({ ...reviewForm, rating: e.target.value })} /></div>
                <div className="sm:col-span-2"><Label>Feedback</Label><Input value={reviewForm.feedback} onChange={(e) => setReviewForm({ ...reviewForm, feedback: e.target.value })} /></div>
              </div>
              <Button size="sm" onClick={() => createReview.mutate()}><Plus className="mr-1 h-3 w-3" />Add review</Button>
              {reviews.map((r) => {
                const emp = employees.find((e) => e.id === r.employee_id);
                return (
                  <div key={r.id} className="rounded-lg border p-3 text-sm">
                    <p className="font-medium">{emp ? `${emp.first_name} ${emp.last_name}` : r.employee_id} · {r.period}</p>
                    <p className="text-muted-foreground">Rating: {r.rating}/5</p>
                  </div>
                );
              })}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2"><Target className="h-5 w-5" />Goals</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <select className="flex h-10 flex-1 rounded-lg border px-3 text-sm" value={goalForm.employee_id} onChange={(e) => setGoalForm({ ...goalForm, employee_id: e.target.value })}>
                  <option value="">Employee...</option>
                  {employees.map((e) => <option key={e.id} value={e.id}>{e.first_name} {e.last_name}</option>)}
                </select>
                <Input placeholder="Goal title" value={goalForm.title} onChange={(e) => setGoalForm({ ...goalForm, title: e.target.value })} />
                <Button size="sm" onClick={() => createGoal.mutate()}>Add</Button>
              </div>
              {goals.map((g) => (
                <div key={g.id} className="flex items-center justify-between rounded-lg border p-3 text-sm">
                  <span>{g.title}</span>
                  <Badge variant="outline">{g.progress}%</Badge>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Training courses ({courses.length})</CardTitle></CardHeader>
          <CardContent>
            {courses.map((c) => (
              <div key={c.id} className="rounded-lg border p-3 text-sm">
                <p className="font-medium">{c.title}</p>
                <p className="text-muted-foreground">{c.duration_hours}h · {c.category || "General"}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
