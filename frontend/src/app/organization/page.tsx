"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Building2, Layers, Plus, Sparkles } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { OrgHierarchyTree } from "@/components/organization/org-hierarchy-tree";
import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { organizationApi } from "@/lib/api/organization";
import { ApiClientError } from "@/lib/api/client";
import { useAuthStore } from "@/stores/auth-store";

export default function OrganizationPage() {
  const accessToken = useAuthStore((s) => s.accessToken)!;
  const isTenantAdmin = useAuthStore((s) => s.isTenantAdmin);
  const hasPermission = useAuthStore((s) => s.hasPermission);
  const canCreate = isTenantAdmin || hasPermission("org:create");
  const canUpdate = isTenantAdmin || hasPermission("org:update");
  const canDelete = isTenantAdmin || hasPermission("org:delete");
  const canManageTypes = isTenantAdmin || hasPermission("org:manage_types");

  const queryClient = useQueryClient();
  const [tab, setTab] = useState<"hierarchy" | "types">("hierarchy");
  const [rootName, setRootName] = useState("");
  const [rootType, setRootType] = useState("");
  const [error, setError] = useState<string | null>(null);

  const { data: nodeTypes = [], isLoading: loadingTypes } = useQuery({
    queryKey: ["org-node-types"],
    queryFn: () => organizationApi.listNodeTypes(accessToken),
    enabled: !!accessToken,
  });

  const { data: tree = [], isLoading: loadingTree } = useQuery({
    queryKey: ["org-tree"],
    queryFn: () => organizationApi.getTree(accessToken),
    enabled: !!accessToken,
  });

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ["org-tree"] });
    queryClient.invalidateQueries({ queryKey: ["org-node-types"] });
  };

  const seedDefaults = useMutation({
    mutationFn: () => organizationApi.seedDefaults(accessToken),
    onSuccess: refresh,
    onError: (e) => setError(e instanceof ApiClientError ? e.message : "Failed to seed defaults"),
  });

  const createRoot = useMutation({
    mutationFn: () =>
      organizationApi.createNode(accessToken, { node_type: rootType, name: rootName }),
    onSuccess: () => {
      setRootName("");
      refresh();
    },
    onError: (e) => setError(e instanceof ApiClientError ? e.message : "Failed to create node"),
  });

  const createChild = useMutation({
    mutationFn: ({
      parentId,
      name,
      type,
    }: {
      parentId: string | null;
      name: string;
      type: string;
    }) =>
      organizationApi.createNode(accessToken, {
        parent_id: parentId ?? undefined,
        node_type: type,
        name,
      }),
    onSuccess: refresh,
    onError: (e) => setError(e instanceof ApiClientError ? e.message : "Failed to create node"),
  });

  const moveNode = useMutation({
    mutationFn: ({ nodeId, parentId }: { nodeId: string; parentId: string | null }) =>
      organizationApi.moveNode(accessToken, nodeId, parentId),
    onSuccess: refresh,
    onError: (e) => setError(e instanceof ApiClientError ? e.message : "Cannot move node here"),
  });

  const renameNode = useMutation({
    mutationFn: ({ nodeId, name }: { nodeId: string; name: string }) =>
      organizationApi.updateNode(accessToken, nodeId, { name }),
    onSuccess: refresh,
  });

  const deleteNode = useMutation({
    mutationFn: (nodeId: string) => organizationApi.deleteNode(accessToken, nodeId),
    onSuccess: refresh,
    onError: (e) => setError(e instanceof ApiClientError ? e.message : "Cannot delete node"),
  });

  const rootTypes = nodeTypes.filter((t) => t.is_root_allowed);

  return (
    <AppShell title="Organization">
      <div className="space-y-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 className="flex items-center gap-2 text-2xl font-bold">
              <Building2 className="h-7 w-7 text-primary" />
              Organization Builder
            </h2>
            <p className="mt-1 text-muted-foreground">
              Create your company hierarchy, drag nodes to reorganize, and add children at any level.
            </p>
          </div>
          {canManageTypes && nodeTypes.length === 0 && (
            <Button onClick={() => seedDefaults.mutate()} disabled={seedDefaults.isPending}>
              <Sparkles className="mr-2 h-4 w-4" />
              {seedDefaults.isPending ? "Setting up..." : "Initialize default levels"}
            </Button>
          )}
        </div>

        {!canCreate && (
          <Card className="border-amber-500/30 bg-amber-500/5">
            <CardContent className="py-4 text-sm text-muted-foreground">
              You have read-only access. Contact a Tenant Administrator to edit the hierarchy.
            </CardContent>
          </Card>
        )}

        {nodeTypes.length === 0 && (
          <Card>
            <CardHeader>
              <CardTitle>No hierarchy levels configured</CardTitle>
              <CardDescription>
                Administrators must define levels (Company → Division → Department → Team) before
                building the tree.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-3">
              {canManageTypes && (
                <Button onClick={() => seedDefaults.mutate()} disabled={seedDefaults.isPending}>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Use default template
                </Button>
              )}
              <Link
                href="/onboarding"
                className="inline-flex h-10 items-center justify-center rounded-lg border border-input bg-background px-4 text-sm font-medium hover:bg-accent"
              >
                Open setup wizard
              </Link>
            </CardContent>
          </Card>
        )}

        {nodeTypes.length > 0 && (
          <>
            <div className="flex gap-2 border-b pb-2">
              <Button
                variant={tab === "hierarchy" ? "default" : "ghost"}
                size="sm"
                onClick={() => setTab("hierarchy")}
              >
                Hierarchy
              </Button>
              <Button
                variant={tab === "types" ? "default" : "ghost"}
                size="sm"
                onClick={() => setTab("types")}
              >
                <Layers className="mr-1 h-4 w-4" />
                Level types
              </Button>
            </div>

            {tab === "hierarchy" && (
              <div className="grid gap-6 lg:grid-cols-3">
                {canCreate && (
                  <Card className="lg:col-span-1">
                    <CardHeader>
                      <CardTitle className="text-base">Add root node</CardTitle>
                      <CardDescription>Top-level company or entity</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div>
                        <Label>Name</Label>
                        <Input
                          value={rootName}
                          onChange={(e) => setRootName(e.target.value)}
                          placeholder="Acme Corporation"
                        />
                      </div>
                      <div>
                        <Label>Type</Label>
                        <select
                          className="mt-1 flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
                          value={rootType}
                          onChange={(e) => setRootType(e.target.value)}
                        >
                          <option value="">Select type...</option>
                          {rootTypes.map((t) => (
                            <option key={t.id} value={t.code}>
                              {t.label}
                            </option>
                          ))}
                        </select>
                      </div>
                      <Button
                        className="w-full"
                        disabled={!rootName || !rootType || createRoot.isPending}
                        onClick={() => createRoot.mutate()}
                      >
                        <Plus className="mr-1 h-4 w-4" />
                        Create root
                      </Button>
                    </CardContent>
                  </Card>
                )}

                <Card className={canCreate ? "lg:col-span-2" : "lg:col-span-3"}>
                  <CardHeader>
                    <CardTitle className="text-base">Hierarchy tree</CardTitle>
                    <CardDescription>
                      {loadingTree
                        ? "Loading..."
                        : `${tree.length} root node(s) · Drag the handle to move nodes`}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <OrgHierarchyTree
                      tree={tree}
                      nodeTypes={nodeTypes}
                      canEdit={canUpdate}
                      onMove={(nodeId, parentId) => moveNode.mutate({ nodeId, parentId })}
                      onAddChild={(parent, name, type) =>
                        createChild.mutate({
                          parentId: parent?.id ?? null,
                          name,
                          type,
                        })
                      }
                      onDelete={(node) => {
                        if (canDelete) deleteNode.mutate(node.id);
                      }}
                      onRename={(node, name) => renameNode.mutate({ nodeId: node.id, name })}
                    />
                  </CardContent>
                </Card>
              </div>
            )}

            {tab === "types" && (
              <Card>
                <CardHeader>
                  <CardTitle>Hierarchy levels</CardTitle>
                  <CardDescription>
                    Metadata-driven types control what can exist under each level
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-3 sm:grid-cols-2">
                    {nodeTypes.map((t) => (
                      <div key={t.id} className="rounded-lg border p-4">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{t.label}</span>
                          <Badge variant="outline">{t.code}</Badge>
                          {t.is_root_allowed && <Badge variant="secondary">Root OK</Badge>}
                        </div>
                        <p className="mt-2 text-xs text-muted-foreground">
                          Children:{" "}
                          {t.allowed_child_types.length
                            ? t.allowed_child_types.join(", ")
                            : "none (leaf level)"}
                        </p>
                      </div>
                    ))}
                  </div>
                  {canManageTypes && (
                    <Link
                      href="/onboarding"
                      className="mt-4 inline-flex h-10 items-center justify-center rounded-lg border border-input bg-background px-4 text-sm font-medium hover:bg-accent"
                    >
                      Customize levels in setup wizard
                    </Link>
                  )}
                </CardContent>
              </Card>
            )}
          </>
        )}

        {error && (
          <p className="text-sm text-destructive" role="alert">
            {error}
          </p>
        )}

        {(loadingTypes || loadingTree) && nodeTypes.length === 0 && (
          <p className="text-sm text-muted-foreground">Loading organization data...</p>
        )}
      </div>
    </AppShell>
  );
}
