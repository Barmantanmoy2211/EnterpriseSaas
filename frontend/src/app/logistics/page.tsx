"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { MapPin, Plus, Ship } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { logisticsApi } from "@/lib/api/logistics";
import { useAuthStore } from "@/stores/auth-store";

export default function LogisticsPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ shipment_number: "", origin: "", destination: "", carrier: "" });

  const { data: shipments = [], isLoading } = useQuery({
    queryKey: ["shipments"],
    queryFn: () => logisticsApi.list(accessToken!),
    enabled: !!accessToken,
  });

  const create = useMutation({
    mutationFn: () => logisticsApi.create(accessToken!, form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["shipments"] });
      setShowForm(false);
      setForm({ shipment_number: "", origin: "", destination: "", carrier: "" });
    },
  });

  return (
    <AppShell title="Logistics">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Logistics & Shipping</h2>
            <p className="text-muted-foreground">{shipments.length} shipment(s)</p>
          </div>
          <Button onClick={() => setShowForm(!showForm)}><Plus className="mr-1 h-4 w-4" />New shipment</Button>
        </div>
        {showForm && (
          <Card>
            <CardHeader><CardTitle>New shipment</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div><Label>Shipment #</Label><Input value={form.shipment_number} onChange={(e) => setForm({ ...form, shipment_number: e.target.value })} /></div>
              <div><Label>Carrier</Label><Input value={form.carrier} onChange={(e) => setForm({ ...form, carrier: e.target.value })} /></div>
              <div><Label>Origin</Label><Input value={form.origin} onChange={(e) => setForm({ ...form, origin: e.target.value })} /></div>
              <div><Label>Destination</Label><Input value={form.destination} onChange={(e) => setForm({ ...form, destination: e.target.value })} /></div>
              <Button disabled={create.isPending} onClick={() => create.mutate()}>Create</Button>
            </CardContent>
          </Card>
        )}
        <div className="space-y-3">
          {isLoading && <p className="text-muted-foreground">Loading...</p>}
          {shipments.map((s) => (
            <Card key={s.id}>
              <CardHeader className="flex flex-row items-center gap-3 pb-2">
                <Ship className="h-5 w-5 text-primary" />
                <div>
                  <CardTitle className="text-base">{s.shipment_number}</CardTitle>
                  <p className="flex items-center gap-1 text-xs text-muted-foreground">
                    <MapPin className="h-3 w-3" />{s.origin || "?"} → {s.destination || "?"}
                  </p>
                </div>
              </CardHeader>
              <CardContent className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">{s.carrier || "—"} · {s.tracking_number || "No tracking"}</p>
                <Badge variant="secondary">{s.status}</Badge>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
