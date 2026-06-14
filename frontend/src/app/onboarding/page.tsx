"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import {
  HierarchyTypeTreeBuilder,
  treeToNodeTypePayloads,
  type HierarchyTypeNode,
} from "@/components/organization/hierarchy-type-tree-builder";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { organizationApi } from "@/lib/api/organization";
import { ApiClientError } from "@/lib/api/client";
import { useAuthStore } from "@/stores/auth-store";

export default function OnboardingPage() {
  const router = useRouter();
  const accessToken = useAuthStore((s) => s.accessToken);
  const [tree, setTree] = useState<HierarchyTypeNode[]>([]);
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
          <h2 className="text-2xl font-bold">Define hierarchy levels</h2>
          <p className="text-muted-foreground">
            Create your own structure — no defaults. After setup, go to Organization → Hierarchy
            to name each node (regions, offices, departments, etc.).
          </p>
        </div>

        <HierarchyTypeTreeBuilder
          tree={tree}
          onChange={setTree}
          formError={formError}
          onFormError={setFormError}
        />

        {error && <p className="text-sm text-destructive">{error}</p>}

        <div className="flex flex-wrap gap-3">
          <Button onClick={handleComplete} disabled={loading}>
            {loading ? "Saving..." : "Save levels & continue"}
          </Button>
          <Button variant="outline" onClick={() => router.push("/dashboard")}>
            Skip for now
          </Button>
        </div>
      </div>
    </AppShell>
  );
}
