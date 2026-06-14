"use client";

import { useQuery } from "@tanstack/react-query";
import { Landmark } from "lucide-react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { financeApi } from "@/lib/api/finance";
import { useAuthStore } from "@/stores/auth-store";

export default function FinancePage() {
  const accessToken = useAuthStore((s) => s.accessToken);

  const { data: accounts = [], isLoading } = useQuery({
    queryKey: ["finance-accounts"],
    queryFn: () => financeApi.listAccounts(accessToken!),
    enabled: !!accessToken,
  });

  return (
    <AppShell title="Finance">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold">Chart of Accounts</h2>
          <p className="text-muted-foreground">{accounts.length} account(s)</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {isLoading && <p className="text-muted-foreground">Loading...</p>}
          {accounts.map((acct) => (
            <Card key={acct.id}>
              <CardHeader className="flex flex-row items-center gap-3 pb-2">
                <Landmark className="h-5 w-5 text-primary" />
                <div>
                  <CardTitle className="text-base">{acct.name}</CardTitle>
                  <p className="text-xs text-muted-foreground">{acct.code}</p>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-lg font-semibold">{acct.currency} {acct.balance.toLocaleString()}</p>
                <Badge variant="outline" className="mt-2 capitalize">{acct.account_type}</Badge>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
