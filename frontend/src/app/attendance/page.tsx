"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Clock, LogIn, LogOut } from "lucide-react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { attendanceApi } from "@/lib/api/hr";
import { employeesApi } from "@/lib/api/employees";
import { useAuthStore } from "@/stores/auth-store";

export default function AttendancePage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();

  const { data: employees = [] } = useQuery({
    queryKey: ["employees"],
    queryFn: () => employeesApi.list(accessToken!),
    enabled: !!accessToken,
  });

  const { data: records = [] } = useQuery({
    queryKey: ["attendance"],
    queryFn: () => attendanceApi.list(accessToken!),
    enabled: !!accessToken,
  });

  const checkIn = useMutation({
    mutationFn: (employeeId: string) => attendanceApi.checkIn(accessToken!, employeeId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["attendance"] }),
  });

  const checkOut = useMutation({
    mutationFn: (employeeId: string) => attendanceApi.checkOut(accessToken!, employeeId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["attendance"] }),
  });

  return (
    <AppShell title="Attendance">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold">Attendance Tracking</h2>
          <p className="text-muted-foreground">Check-in/out and daily attendance records</p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {employees.filter((e) => e.status === "active").map((emp) => (
            <Card key={emp.id}>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">{emp.first_name} {emp.last_name}</CardTitle>
              </CardHeader>
              <CardContent className="flex gap-2">
                <Button size="sm" variant="outline" onClick={() => checkIn.mutate(emp.id)} disabled={checkIn.isPending}>
                  <LogIn className="mr-1 h-3 w-3" />In
                </Button>
                <Button size="sm" variant="outline" onClick={() => checkOut.mutate(emp.id)} disabled={checkOut.isPending}>
                  <LogOut className="mr-1 h-3 w-3" />Out
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Clock className="h-5 w-5" />Recent records</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {records.map((r) => {
              const emp = employees.find((e) => e.id === r.employee_id);
              return (
                <div key={r.id} className="flex items-center justify-between rounded-lg border p-3 text-sm">
                  <span>{emp ? `${emp.first_name} ${emp.last_name}` : r.employee_id}</span>
                  <span className="text-muted-foreground">{r.date}</span>
                  <Badge variant="secondary">{r.status}</Badge>
                  <span className="font-mono text-xs">{r.hours_worked}h</span>
                </div>
              );
            })}
            {records.length === 0 && <p className="text-sm text-muted-foreground">No attendance records</p>}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
