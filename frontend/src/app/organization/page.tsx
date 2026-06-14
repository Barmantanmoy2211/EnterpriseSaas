"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Building2, Layers, Plus, Save } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import {
  HierarchyTypeTreeBuilder,
  nodeTypesToTree,
  treeToNodeTypePayloads,
  type HierarchyTypeNode,
} from "@/components/organization/hierarchy-type-tree-builder";
import { OrgHierarchyTree } from "@/components/organization/org-hierarchy-tree";
import { AppShell } from "@/components/layout/app-shell";
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
  const [tab, setTab] = useState<"hierarchy" | "types">("types");
  const [rootName, setRootName] = useState("");
  const [rootType, setRootType] = useState("");
  const [typeTree, setTypeTree] = useState<HierarchyTypeNode[]>([]);
  const [typeFormError, setTypeFormError] = useState<string | null>(null);
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

  useEffect(() => {
    if (nodeTypes.length > 0) {
      setTypeTree(nodeTypesToTree(nodeTypes));
      if (tree.length > 0) setTab("hierarchy");
    }
  }, [nodeTypes, tree.length]);

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ["org-tree"] });
    queryClient.invalidateQueries({ queryKey: ["org-node-types"] });
  };

  const saveTypes = useMutation({
    mutationFn: async () => {
      const payloads = treeToNodeTypePayloads(typeTree);
      const existingByCode = new Map(nodeTypes.map((t) => [t.code, t]));

      for (const p of payloads) {
        const existing = existingByCode.get(p.code);
        if (existing) {
          await organizationApi.updateNodeType(accessToken, existing.id, {
            label: p.label,
            is_root_allowed: p.is_root_allowed,
            allowed_child_types: p.allowed_child_types,
          });
        } else {
          await organizationApi.createNodeType(accessToken, {
            code: p.code,
            label: p.label,
            is_root_allowed: p.is_root_allowed,
            allowed_child_types: p.allowed_child_types,
            schema: {},
          });
        }
      }

      const payloadCodes = new Set(payloads.map((p) => p.code));
      for (const t of nodeTypes) {
        if (!payloadCodes.has(t.code) && tree.length === 0) {
          await organizationApi.deleteNodeType(accessToken, t.id);
        }
      }
    },
    onSuccess: () => {
      setError(null);
      refresh();
    },
    onError: (e) => setError(e instanceof ApiClientError ? e.message : "Failed to save level types"),
  });

  const createRoot = useMutation({
    mutationFn: (nodeType: string) =>
      organizationApi.createNode(accessToken, { node_type: nodeType, name: rootName }),
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
  const singleRootType = rootTypes.length === 1 ? rootTypes[0].code : "";

  return (
    <AppShell title="Organization">
      <div className="space-y-6">
        <div>
          <h2 className="flex items-center gap-2 text-2xl font-bold">
            <Building2 className="h-7 w-7 text-primary" />
            Organization
          </h2>
          <p className="mt-1 text-muted-foreground">
            First define your hierarchy <strong>level types</strong> (structure). Then in the{" "}
            <strong>Hierarchy</strong> tab, name each node (regions, offices, teams, etc.).
          </p>
        </div>

        {!canCreate && nodeTypes.length > 0 && (
          <Card className="border-amber-500/30 bg-amber-500/5">
            <CardContent className="py-4 text-sm text-muted-foreground">
              You have read-only access. Contact a Tenant Administrator to edit the hierarchy.
            </CardContent>
          </Card>
        )}

        <div className="flex gap-2 border-b pb-2">
          <Button
            variant={tab === "types" ? "default" : "ghost"}
            size="sm"
            onClick={() => setTab("types")}
          >
            <Layers className="mr-1 h-4 w-4" />
            Level types
          </Button>
          <Button
            variant={tab === "hierarchy" ? "default" : "ghost"}
            size="sm"
            onClick={() => setTab("hierarchy")}
            disabled={nodeTypes.length === 0 && typeTree.length === 0}
          >
            Hierarchy
          </Button>
        </div>

        {tab === "types" && (
          <div className="space-y-4">
            {nodeTypes.length === 0 && typeTree.length === 0 && (
              <Card className="border-dashed">
                <CardHeader>
                  <CardTitle className="text-base">No level types yet</CardTitle>
                  <CardDescription>
                    Build your own structure — e.g. Company → Region → Branch → Team. Nothing is
                    pre-filled; you decide the levels and labels.
                  </CardDescription>
                </CardHeader>
              </Card>
            )}

            {canManageTypes ? (
              <>
                <HierarchyTypeTreeBuilder
                  tree={typeTree}
                  onChange={setTypeTree}
                  formError={typeFormError}
                  onFormError={setTypeFormError}
                />
                <Button
                  onClick={() => saveTypes.mutate()}
                  disabled={typeTree.length === 0 || saveTypes.isPending}
                >
                  <Save className="mr-2 h-4 w-4" />
                  {saveTypes.isPending ? "Saving..." : "Save level types"}
                </Button>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">
                You need permission to manage hierarchy level types.
              </p>
            )}
          </div>
        )}

        {tab === "hierarchy" && (
          <>
            {nodeTypes.length === 0 ? (
              <Card>
                <CardContent className="py-8 text-center text-sm text-muted-foreground">
                  Save level types first, then return here to name your hierarchy nodes.
                  <div className="mt-4">
                    <Button variant="outline" size="sm" onClick={() => setTab("types")}>
                      Go to Level types
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-6 lg:grid-cols-3">
                {canCreate && tree.length === 0 && (
                  <Card className="lg:col-span-1">
                    <CardHeader>
                      <CardTitle className="text-base">Create root</CardTitle>
                      <CardDescription>Name your top-level entity</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div>
                        <Label>Name</Label>
                        <Input
                          value={rootName}
                          onChange={(e) => setRootName(e.target.value)}
                          placeholder="Acme Global"
                        />
                      </div>
                      {rootTypes.length > 1 ? (
                        <div>
                          <Label>Level type</Label>
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
                      ) : (
                        singleRootType && (
                          <p className="text-xs text-muted-foreground">
                            Level: {rootTypes[0]?.label}
                          </p>
                        )
                      )}
                      <Button
                        className="w-full"
                        disabled={
                          !rootName ||
                          (!rootType && !singleRootType) ||
                          createRoot.isPending
                        }
                        onClick={() => {
                          const type = rootType || singleRootType;
                          if (type) createRoot.mutate(type);
                        }}
                      >
                        <Plus className="mr-1 h-4 w-4" />
                        Create root
                      </Button>
                    </CardContent>
                  </Card>
                )}

                <Card className={canCreate && tree.length === 0 ? "lg:col-span-2" : "lg:col-span-3"}>
                  <CardHeader>
                    <CardTitle className="text-base">Hierarchy tree</CardTitle>
                    <CardDescription>
                      {loadingTree
                        ? "Loading..."
                        : `${tree.length} root node(s) — add children and name each level (region, office, etc.)`}
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

        {nodeTypes.length === 0 && canManageTypes && (
          <p className="text-sm text-muted-foreground">
            Or use the{" "}
            <Link href="/onboarding" className="text-primary underline">
              setup wizard
            </Link>{" "}
            to configure levels during onboarding.
          </p>
        )}
      </div>
    </AppShell>
  );
}
