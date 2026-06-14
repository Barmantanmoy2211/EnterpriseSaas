"use client";

import { useQuery } from "@tanstack/react-query";
import { Building2, ChevronRight } from "lucide-react";

import { organizationApi, type OrgNode } from "@/lib/api/organization";
import { useAuthStore } from "@/stores/auth-store";
import { useOrgContextStore } from "@/stores/org-context-store";
import { cn } from "@/lib/utils";

function findNodePath(tree: OrgNode[], targetId: string, trail: OrgNode[] = []): OrgNode[] | null {
  for (const node of tree) {
    const next = [...trail, node];
    if (node.id === targetId) return next;
    const found = findNodePath(node.children, targetId, next);
    if (found) return found;
  }
  return null;
}

function flattenNodes(tree: OrgNode[], depth = 0): { node: OrgNode; depth: number; path: string }[] {
  const items: { node: OrgNode; depth: number; path: string }[] = [];
  for (const node of tree) {
    const path = node.name;
    items.push({ node, depth, path });
    for (const child of flattenNodes(node.children, depth + 1)) {
      items.push({
        ...child,
        path: `${path} › ${child.path}`,
      });
    }
  }
  return items;
}

export function OrgHierarchyPicker({ className }: { className?: string }) {
  const accessToken = useAuthStore((s) => s.accessToken);
  const isTenantAdmin = useAuthStore((s) => s.isTenantAdmin);
  const scopeNodeIds = useAuthStore((s) => s.scopeNodeIds);
  const selectedNodeId = useOrgContextStore((s) => s.selectedNodeId);
  const setSelectedNodeId = useOrgContextStore((s) => s.setSelectedNodeId);

  const { data: tree = [] } = useQuery({
    queryKey: ["org-tree"],
    queryFn: () => organizationApi.getTree(accessToken!),
    enabled: !!accessToken,
  });

  if (tree.length === 0) return null;

  const scopeSet = isTenantAdmin || scopeNodeIds.length === 0 ? null : new Set(scopeNodeIds);
  const options = flattenNodes(tree).filter(
    (o) => !scopeSet || scopeSet.has(o.node.id),
  );

  const activePath =
    selectedNodeId && findNodePath(tree, selectedNodeId)?.map((n) => n.name).join(" › ");

  return (
    <div className={cn("flex min-w-0 items-center gap-2", className)}>
      <Building2 className="h-4 w-4 shrink-0 text-muted-foreground" />
      <select
        className="h-8 max-w-[220px] truncate rounded-md border border-input bg-background px-2 text-xs sm:max-w-xs sm:text-sm"
        value={selectedNodeId ?? ""}
        onChange={(e) => setSelectedNodeId(e.target.value || null)}
        title="Hierarchy context"
      >
        <option value="">{isTenantAdmin ? "All organization" : "Select hierarchy scope"}</option>
        {options.map((o) => (
          <option key={o.node.id} value={o.node.id}>
            {"—".repeat(o.depth)}
            {o.depth > 0 ? " " : ""}
            {o.path}
          </option>
        ))}
      </select>
      {activePath && (
        <span className="hidden min-w-0 items-center gap-1 text-xs text-muted-foreground lg:flex">
          <ChevronRight className="h-3 w-3" />
          <span className="truncate">{activePath}</span>
        </span>
      )}
    </div>
  );
}
