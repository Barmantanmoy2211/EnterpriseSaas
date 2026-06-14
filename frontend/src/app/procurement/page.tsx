"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, ShoppingCart, Truck } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { procurementApi } from "@/lib/api/procurement";
import { useAuthStore } from "@/stores/auth-store";

export default function ProcurementPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", code: "", contact_email: "" });

  const { data: suppliers = [], isLoading: loadingSuppliers } = useQuery({
    queryKey: ["suppliers"],
    queryFn: () => procurementApi.listSuppliers(accessToken!),
    enabled: !!accessToken,
  });

  const { data: orders = [], isLoading: loadingOrders } = useQuery({
    queryKey: ["purchase-orders"],
    queryFn: () => procurementApi.listOrders(accessToken!),
    enabled: !!accessToken,
  });

  const create = useMutation({
    mutationFn: () => procurementApi.createSupplier(accessToken!, form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["suppliers"] });
      setShowForm(false);
      setForm({ name: "", code: "", contact_email: "" });
    },
  });

  return (
    <AppShell title="Procurement">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Procurement</h2>
            <p className="text-muted-foreground">{suppliers.length} supplier(s) · {orders.length} PO(s)</p>
          </div>
          <Button onClick={() => setShowForm(!showForm)}><Plus className="mr-1 h-4 w-4" />Add supplier</Button>
        </div>
        {showForm && (
          <Card>
            <CardHeader><CardTitle>New supplier</CardTitle></CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div><Label>Name</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
              <div><Label>Code</Label><Input value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} /></div>
              <div><Label>Email</Label><Input value={form.contact_email} onChange={(e) => setForm({ ...form, contact_email: e.target.value })} /></div>
              <Button disabled={create.isPending} onClick={() => create.mutate()}>Create</Button>
            </CardContent>
          </Card>
        )}
        <div className="grid gap-6 lg:grid-cols-2">
          <div>
            <h3 className="mb-3 font-semibold">Suppliers</h3>
            <div className="space-y-3">
              {loadingSuppliers && <p className="text-muted-foreground">Loading...</p>}
              {suppliers.map((s) => (
                <Card key={s.id}>
                  <CardHeader className="flex flex-row items-center gap-3 pb-2">
                    <Truck className="h-5 w-5 text-primary" />
                    <CardTitle className="text-base">{s.name}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">{s.contact_email || "—"}</p>
                    <Badge variant="secondary" className="mt-2">{s.status}</Badge>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
          <div>
            <h3 className="mb-3 font-semibold">Purchase Orders</h3>
            <div className="space-y-3">
              {loadingOrders && <p className="text-muted-foreground">Loading...</p>}
              {orders.map((o) => (
                <Card key={o.id}>
                  <CardHeader className="flex flex-row items-center gap-3 pb-2">
                    <ShoppingCart className="h-5 w-5 text-primary" />
                    <CardTitle className="text-base">{o.po_number}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm">{o.currency} {o.total_amount.toLocaleString()}</p>
                    <Badge variant="outline" className="mt-2">{o.status}</Badge>
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
