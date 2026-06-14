"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import {
  createDefaultTypeTree,
  HierarchyTypeTreeBuilder,
  treeToNodeTypePayloads,
  type HierarchyTypeNode,
} from "@/components/organization/hierarchy-type-tree-builder";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { organizationApi } from "@/lib/api/organization";
import { ApiClientError } from "@/lib/api/client";
import { useAuthStore } from "@/stores/auth-store";

export default function OnboardingPage() {
  const router = useRouter();
  const accessToken = useAuthStore((s) => s.accessToken);
  const [tree, setTree] = useState<HierarchyTypeNode[]>(createDefaultTypeTree);
  const [companyName, setCompanyName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleComplete = async () => {
    if (!accessToken) return;
    setError(null);
    setLoading(true);

    const payloads = treeToNodeTypePayloads(tree);
    if (payloads.length === 0) {
      setError("Add at least one hierarchy level before completing setup.");
      setLoading(false);
      return;
    }

    try {
      for (const t of payloads) {
        await organizationApi.createNodeType(accessToken, {
          code: t.code,
          label: t.label,
          is_root_allowed: t.is_root_allowed,
          allowed_child_types: t.allowed_child_types,
          schema: {},
        });
      }

      if (companyName.trim()) {
        const rootType = payloads.find((t) => t.is_root_allowed);
        if (rootType) {
          await organizationApi.createNode(accessToken, {
            node_type: rootType.code,
            name: companyName.trim(),
          });
        }
      }

      router.push("/organization");
    } catch (e) {
      setError(e instanceof ApiClientError ? e.message : "Setup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell title="Workspace Setup">
      <div className="mx-auto max-w-6xl space-y-6">
        <div>
          <h2 className="text-2xl font-bold">Configure your organization</h2>
          <p className="text-muted-foreground">
            Build your hierarchy as a tree — add a root level, then add children under each node.
            Parent relationships use a picklist, not comma-separated text.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Root organization</CardTitle>
            <CardDescription>Name your top-level company entity (optional)</CardDescription>
          </CardHeader>
          <CardContent>
            <Label htmlFor="company">Company name</Label>
            <Input
              id="company"
              className="mt-2 max-w-md"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="Acme Corporation"
            />
          </CardContent>
        </Card>

        <HierarchyTypeTreeBuilder
          tree={tree}
          onChange={setTree}
          formError={formError}
          onFormError={setFormError}
        />

        {error && <p className="text-sm text-destructive">{error}</p>}

        <div className="flex flex-wrap gap-3">
          <Button onClick={handleComplete} disabled={loading}>
            {loading ? "Setting up..." : "Complete setup"}
          </Button>
          <Button variant="outline" onClick={() => router.push("/dashboard")}>
            Skip for now
          </Button>
        </div>
      </div>
    </AppShell>
  );
}
