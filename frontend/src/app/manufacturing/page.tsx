"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Factory, Plus } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { manufacturingApi } from "@/lib/api/manufacturing";
import { useAuthStore } from "@/stores/auth-store";

export default function ManufacturingPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ product_sku: "", name: "", description: "" });

  const { data: boms = [], isLoading: loadingBoms } = useQuery({
    queryKey: ["boms"],
    queryFn: () => manufacturingApi.listBoms(accessToken!),
    enabled: !!accessToken,
  });

  const { data: orders = [], isLoading: loadingOrders } = useQuery({
    queryKey: ["production-orders"],
    queryFn: () => manufacturingApi.listOrders(accessToken!),
    enabled: !!accessToken,
  });

  const create = useMutation({
    mutationFn: () => manufacturingApi.createBom(accessToken!, form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["boms"] });
      setShowForm(false);
      setForm({ product_sku: "", name: "", description: "" });
    },
  });

  return (
    <AppShell title="Manufacturing">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Manufacturing</h2>
            <p className="text-muted-foreground">{boms.length} BOM(s) · {orders.length} production order(s)</p>
          </div>
          <Button onClick={() => setShowForm(!showForm)}><Plus className="mr-1 h-4 w-4" />Add BOM</Button>
        </div>
        {showForm && (
          <Card>
            <CardHeader><CardTitle>New bill of materials</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div><Label>Product SKU</Label><Input value={form.product_sku} onChange={(e) => setForm({ ...form, product_sku: e.target.value })} /></div>
              <div><Label>Name</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
              <Button disabled={create.isPending} onClick={() => create.mutate()}>Create</Button>
            </CardContent>
          </Card>
        )}
        <div className="grid gap-6 lg:grid-cols-2">
          <div>
            <h3 className="mb-3 font-semibold">Bills of Materials</h3>
            <div className="space-y-3">
              {loadingBoms && <p className="text-muted-foreground">Loading...</p>}
              {boms.map((bom) => (
                <Card key={bom.id}>
                  <CardHeader className="flex flex-row items-center gap-3 pb-2">
                    <Factory className="h-5 w-5 text-primary" />
                    <div>
                      <CardTitle className="text-base">{bom.name}</CardTitle>
                      <p className="text-xs text-muted-foreground">{bom.product_sku}</p>
                    </div>
                  </CardHeader>
                  <CardContent><Badge variant="outline">v{bom.version}</Badge></CardContent>
                </Card>
              ))}
            </div>
          </div>
          <div>
            <h3 className="mb-3 font-semibold">Production Orders</h3>
            <div className="space-y-3">
              {loadingOrders && <p className="text-muted-foreground">Loading...</p>}
              {orders.map((o) => (
                <Card key={o.id}>
                  <CardContent className="flex items-center justify-between pt-6">
                    <div>
                      <p className="font-medium">{o.order_number}</p>
                      <p className="text-sm text-muted-foreground">Qty: {o.quantity}</p>
                    </div>
                    <Badge variant="secondary">{o.status}</Badge>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
