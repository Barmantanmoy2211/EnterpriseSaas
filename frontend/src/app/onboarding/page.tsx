"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Plus, Trash2 } from "lucide-react";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { organizationApi } from "@/lib/api/organization";
import { ApiClientError } from "@/lib/api/client";
import { useAuthStore } from "@/stores/auth-store";

interface NodeTypeDraft {
  code: string;
  label: string;
  is_root_allowed: boolean;
  allowed_child_types: string;
}

const DEFAULT_TYPES: NodeTypeDraft[] = [
  { code: "company", label: "Company", is_root_allowed: true, allowed_child_types: "division" },
  { code: "division", label: "Division", is_root_allowed: false, allowed_child_types: "department" },
  { code: "department", label: "Department", is_root_allowed: false, allowed_child_types: "team" },
  { code: "team", label: "Team", is_root_allowed: false, allowed_child_types: "" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const accessToken = useAuthStore((s) => s.accessToken);
  const [types, setTypes] = useState<NodeTypeDraft[]>(DEFAULT_TYPES);
  const [companyName, setCompanyName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const updateType = (index: number, field: keyof NodeTypeDraft, value: string | boolean) => {
    setTypes((prev) => prev.map((t, i) => (i === index ? { ...t, [field]: value } : t)));
  };

  const addType = () => {
    setTypes((prev) => [
      ...prev,
      { code: "", label: "", is_root_allowed: false, allowed_child_types: "" },
    ]);
  };

  const removeType = (index: number) => {
    setTypes((prev) => prev.filter((_, i) => i !== index));
  };

  const handleComplete = async () => {
    if (!accessToken) return;
    setError(null);
    setLoading(true);
    try {
      for (const t of types) {
        if (!t.code || !t.label) continue;
        await organizationApi.createNodeType(accessToken, {
          code: t.code,
          label: t.label,
          is_root_allowed: t.is_root_allowed,
          allowed_child_types: t.allowed_child_types
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean),
          schema: {},
        });
      }

      if (companyName.trim()) {
        const rootType = types.find((t) => t.is_root_allowed);
        if (rootType) {
          await organizationApi.createNode(accessToken, {
            node_type: rootType.code,
            name: companyName.trim(),
          });
        }
      }

      router.push("/dashboard");
    } catch (e) {
      setError(e instanceof ApiClientError ? e.message : "Setup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell title="Workspace Setup">
      <div className="mx-auto max-w-3xl space-y-6">
        <div>
          <h2 className="text-2xl font-bold">Configure your organization</h2>
          <p className="text-muted-foreground">
            Define your hierarchy levels. These are fully customizable—nothing is hardcoded.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Root organization</CardTitle>
            <CardDescription>Name your top-level entity</CardDescription>
          </CardHeader>
          <CardContent>
            <Label htmlFor="company">Company name</Label>
            <Input
              id="company"
              className="mt-2"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="Acme Corporation"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Hierarchy levels</CardTitle>
              <CardDescription>Define node types and allowed parent-child relationships</CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={addType}>
              <Plus className="h-4 w-4" />
              Add level
            </Button>
          </CardHeader>
          <CardContent className="space-y-4">
            {types.map((type, index) => (
              <div key={index} className="grid gap-3 rounded-lg border p-4 sm:grid-cols-2">
                <div>
                  <Label>Code</Label>
                  <Input
                    value={type.code}
                    onChange={(e) => updateType(index, "code", e.target.value)}
                    placeholder="division"
                  />
                </div>
                <div>
                  <Label>Label</Label>
                  <Input
                    value={type.label}
                    onChange={(e) => updateType(index, "label", e.target.value)}
                    placeholder="Division"
                  />
                </div>
                <div className="sm:col-span-2">
                  <Label>Allowed child types (comma-separated)</Label>
                  <Input
                    value={type.allowed_child_types}
                    onChange={(e) => updateType(index, "allowed_child_types", e.target.value)}
                    placeholder="department, team"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id={`root-${index}`}
                    checked={type.is_root_allowed}
                    onChange={(e) => updateType(index, "is_root_allowed", e.target.checked)}
                  />
                  <Label htmlFor={`root-${index}`}>Allow at root level</Label>
                </div>
                {types.length > 1 && (
                  <Button variant="ghost" size="sm" onClick={() => removeType(index)}>
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                )}
              </div>
            ))}
          </CardContent>
        </Card>

        {error && <p className="text-sm text-destructive">{error}</p>}

        <div className="flex gap-3">
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
