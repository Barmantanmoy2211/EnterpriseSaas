"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Calendar, Plus } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { employeesApi } from "@/lib/api/employees";
import { leaveApi } from "@/lib/api/hr";
import { useAuthStore } from "@/stores/auth-store";

export default function LeavePage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    employee_id: "",
    leave_type_id: "",
    start_date: "",
    end_date: "",
    days: "1",
    reason: "",
  });

  const { data: employees = [] } = useQuery({
    queryKey: ["employees"],
    queryFn: () => employeesApi.list(accessToken!),
    enabled: !!accessToken,
  });

  const { data: types = [] } = useQuery({
    queryKey: ["leave-types"],
    queryFn: () => leaveApi.listTypes(accessToken!),
    enabled: !!accessToken,
  });

  const { data: requests = [] } = useQuery({
    queryKey: ["leave-requests"],
    queryFn: () => leaveApi.listRequests(accessToken!),
    enabled: !!accessToken,
  });

  const create = useMutation({
    mutationFn: () =>
      leaveApi.createRequest(accessToken!, {
        ...form,
        days: parseFloat(form.days),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["leave-requests"] });
      setShowForm(false);
    },
  });

  return (
    <AppShell title="Leave Management">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Leave Requests</h2>
            <p className="text-muted-foreground">Workflow-integrated leave management</p>
          </div>
          <Button onClick={() => setShowForm(!showForm)}>
            <Plus className="mr-1 h-4 w-4" />
            New request
          </Button>
        </div>

        <div className="flex flex-wrap gap-2">
          {types.map((t) => (
            <Badge key={t.id} variant="outline">{t.name} ({t.days_allowed}d)</Badge>
          ))}
        </div>

        {showForm && (
          <Card>
            <CardHeader><CardTitle>Submit leave request</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label>Employee</Label>
                <select className="mt-1 flex h-10 w-full rounded-lg border px-3 text-sm" value={form.employee_id} onChange={(e) => setForm({ ...form, employee_id: e.target.value })}>
                  <option value="">Select...</option>
                  {employees.map((e) => <option key={e.id} value={e.id}>{e.first_name} {e.last_name}</option>)}
                </select>
              </div>
              <div>
                <Label>Leave type</Label>
                <select className="mt-1 flex h-10 w-full rounded-lg border px-3 text-sm" value={form.leave_type_id} onChange={(e) => setForm({ ...form, leave_type_id: e.target.value })}>
                  <option value="">Select...</option>
                  {types.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
                </select>
              </div>
              <div><Label>Start date</Label><Input type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} /></div>
              <div><Label>End date</Label><Input type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} /></div>
              <div><Label>Days</Label><Input type="number" value={form.days} onChange={(e) => setForm({ ...form, days: e.target.value })} /></div>
              <div className="sm:col-span-2"><Label>Reason</Label><Input value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} /></div>
              <Button onClick={() => create.mutate()} disabled={create.isPending}>Submit</Button>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><Calendar className="h-5 w-5" />Requests</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {requests.map((r) => {
              const emp = employees.find((e) => e.id === r.employee_id);
              const lt = types.find((t) => t.id === r.leave_type_id);
              return (
                <div key={r.id} className="flex items-center justify-between rounded-lg border p-3">
                  <div>
                    <p className="font-medium">{emp ? `${emp.first_name} ${emp.last_name}` : r.employee_id}</p>
                    <p className="text-sm text-muted-foreground">{lt?.name} · {r.start_date} → {r.end_date} ({r.days}d)</p>
                  </div>
                  <Badge variant={r.status === "approved" ? "default" : "secondary"}>{r.status}</Badge>
                </div>
              );
            })}
            {requests.length === 0 && <p className="text-sm text-muted-foreground">No leave requests</p>}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
