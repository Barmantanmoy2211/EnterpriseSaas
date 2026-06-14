"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Package, Plus } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { inventoryApi } from "@/lib/api/inventory";
import { useAuthStore } from "@/stores/auth-store";

export default function InventoryPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ sku: "", name: "", quantity: 0, unit: "ea", warehouse_location: "" });

  const { data: items = [], isLoading } = useQuery({
    queryKey: ["inventory"],
    queryFn: () => inventoryApi.list(accessToken!),
    enabled: !!accessToken,
  });

  const create = useMutation({
    mutationFn: () => inventoryApi.create(accessToken!, form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
      setShowForm(false);
      setForm({ sku: "", name: "", quantity: 0, unit: "ea", warehouse_location: "" });
    },
  });

  return (
    <AppShell title="Inventory">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Inventory Management</h2>
            <p className="text-muted-foreground">{items.length} item(s)</p>
          </div>
          <Button onClick={() => setShowForm(!showForm)}><Plus className="mr-1 h-4 w-4" />Add item</Button>
        </div>
        {showForm && (
          <Card>
            <CardHeader><CardTitle>New inventory item</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div><Label>SKU</Label><Input value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} /></div>
              <div><Label>Name</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
              <div><Label>Quantity</Label><Input type="number" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: Number(e.target.value) })} /></div>
              <div><Label>Location</Label><Input value={form.warehouse_location} onChange={(e) => setForm({ ...form, warehouse_location: e.target.value })} /></div>
              <Button disabled={create.isPending} onClick={() => create.mutate()}>Create</Button>
            </CardContent>
          </Card>
        )}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {isLoading && <p className="text-muted-foreground">Loading...</p>}
          {items.map((item) => (
            <Card key={item.id}>
              <CardHeader className="flex flex-row items-center gap-3 pb-2">
                <Package className="h-5 w-5 text-primary" />
                <div>
                  <CardTitle className="text-base">{item.name}</CardTitle>
                  <p className="text-xs text-muted-foreground">{item.sku}</p>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm">{item.quantity} {item.unit}</p>
                <p className="text-xs text-muted-foreground">{item.warehouse_location || "—"}</p>
                <Badge variant="secondary" className="mt-2">{item.status}</Badge>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
