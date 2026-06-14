"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChevronDown, ChevronRight, Plus, Trash2 } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { OrgNode, OrgNodeType } from "@/lib/api/organization";
import { organizationApi } from "@/lib/api/organization";
import { useAuthStore } from "@/stores/auth-store";

function OrgTreeNode({
  node,
  nodeTypes,
  token,
  onRefresh,
}: {
  node: OrgNode;
  nodeTypes: OrgNodeType[];
  token: string;
  onRefresh: () => void;
}) {
  const [expanded, setExpanded] = useState(true);
  const [adding, setAdding] = useState(false);
  const [childName, setChildName] = useState("");
  const [childType, setChildType] = useState("");

  const parentType = nodeTypes.find((t) => t.code === node.node_type);
  const allowedChildren = parentType?.allowed_child_types ?? [];

  const createChild = useMutation({
    mutationFn: () =>
      organizationApi.createNode(token, {
        parent_id: node.id,
        node_type: childType,
        name: childName,
      }),
    onSuccess: () => {
      setAdding(false);
      setChildName("");
      onRefresh();
    },
  });

  const deleteNode = useMutation({
    mutationFn: () => organizationApi.deleteNode(token, node.id),
    onSuccess: onRefresh,
  });

  return (
    <div className="ml-4 border-l pl-4">
      <div className="flex items-center gap-2 py-1">
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className="text-muted-foreground hover:text-foreground"
        >
          {node.children.length > 0 ? (
            expanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />
          ) : (
            <span className="inline-block w-4" />
          )}
        </button>
        <span className="font-medium">{node.name}</span>
        <Badge variant="secondary">{node.node_type}</Badge>
        {allowedChildren.length > 0 && (
          <Button variant="ghost" size="sm" onClick={() => setAdding(!adding)}>
            <Plus className="h-3 w-3" />
          </Button>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => deleteNode.mutate()}
          disabled={node.children.length > 0}
        >
          <Trash2 className="h-3 w-3 text-destructive" />
        </Button>
      </div>

      {adding && (
        <div className="mb-2 ml-6 flex flex-wrap items-end gap-2 rounded-lg border bg-muted/30 p-3">
          <div>
            <Label className="text-xs">Name</Label>
            <Input value={childName} onChange={(e) => setChildName(e.target.value)} className="h-8" />
          </div>
          <div>
            <Label className="text-xs">Type</Label>
            <select
              className="flex h-8 rounded-lg border border-input bg-background px-2 text-sm"
              value={childType}
              onChange={(e) => setChildType(e.target.value)}
            >
              <option value="">Select...</option>
              {allowedChildren.map((code) => {
                const nt = nodeTypes.find((t) => t.code === code);
                return (
                  <option key={code} value={code}>
                    {nt?.label ?? code}
                  </option>
                );
              })}
            </select>
          </div>
          <Button
            size="sm"
            disabled={!childName || !childType || createChild.isPending}
            onClick={() => createChild.mutate()}
          >
            Add
          </Button>
        </div>
      )}

      {expanded &&
        node.children.map((child) => (
          <OrgTreeNode
            key={child.id}
            node={child}
            nodeTypes={nodeTypes}
            token={token}
            onRefresh={onRefresh}
          />
        ))}
    </div>
  );
}

export default function OrganizationPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const queryClient = useQueryClient();
  const [rootName, setRootName] = useState("");
  const [rootType, setRootType] = useState("");

  const { data: nodeTypes = [] } = useQuery({
    queryKey: ["org-node-types"],
    queryFn: () => organizationApi.listNodeTypes(accessToken!),
    enabled: !!accessToken,
  });

  const { data: tree = [], isLoading } = useQuery({
    queryKey: ["org-tree"],
    queryFn: () => organizationApi.getTree(accessToken!),
    enabled: !!accessToken,
  });

  const refresh = () => queryClient.invalidateQueries({ queryKey: ["org-tree"] });

  const createRoot = useMutation({
    mutationFn: () =>
      organizationApi.createNode(accessToken!, {
        node_type: rootType,
        name: rootName,
      }),
    onSuccess: () => {
      setRootName("");
      refresh();
    },
  });

  const rootTypes = nodeTypes.filter((t) => t.is_root_allowed);

  return (
    <AppShell title="Organization">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold">Organization Builder</h2>
          <p className="text-muted-foreground">
            Build your unlimited-depth hierarchy. Node types are defined by your tenant metadata.
          </p>
        </div>

        {nodeTypes.length === 0 && (
          <Card>
            <CardHeader>
              <CardTitle>No node types configured</CardTitle>
              <CardDescription>
                Complete onboarding or add node types via the API to start building your hierarchy.
              </CardDescription>
            </CardHeader>
          </Card>
        )}

        {tree.length === 0 && rootTypes.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Create root node</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap items-end gap-3">
              <div>
                <Label>Name</Label>
                <Input value={rootName} onChange={(e) => setRootName(e.target.value)} />
              </div>
              <div>
                <Label>Type</Label>
                <select
                  className="flex h-10 rounded-lg border border-input bg-background px-3 text-sm"
                  value={rootType}
                  onChange={(e) => setRootType(e.target.value)}
                >
                  <option value="">Select...</option>
                  {rootTypes.map((t) => (
                    <option key={t.id} value={t.code}>
                      {t.label}
                    </option>
                  ))}
                </select>
              </div>
              <Button
                disabled={!rootName || !rootType || createRoot.isPending}
                onClick={() => createRoot.mutate()}
              >
                Create
              </Button>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Hierarchy</CardTitle>
            <CardDescription>
              {isLoading ? "Loading..." : `${tree.length} root node(s)`}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {tree.map((node) => (
              <OrgTreeNode
                key={node.id}
                node={node}
                nodeTypes={nodeTypes}
                token={accessToken!}
                onRefresh={refresh}
              />
            ))}
            {tree.length === 0 && !isLoading && nodeTypes.length > 0 && (
              <p className="text-sm text-muted-foreground">No nodes yet. Create a root node above.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
