"use client";

import { ChevronDown, ChevronRight, GitBranch, Plus, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

export interface HierarchyTypeNode {
  id: string;
  code: string;
  label: string;
  children: HierarchyTypeNode[];
}

export interface HierarchyTypePayload {
  code: string;
  label: string;
  is_root_allowed: boolean;
  allowed_child_types: string[];
}

const CODE_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

function newId() {
  return `type-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}

export function createDefaultTypeTree(): HierarchyTypeNode[] {
  return [];
}

/** Reconstruct a type tree from flat API node types (roots → children via allowed_child_types). */
export function nodeTypesToTree(types: { id: string; code: string; label: string; allowed_child_types: string[]; is_root_allowed: boolean }[]): HierarchyTypeNode[] {
  const byCode = new Map(types.map((t) => [t.code, t]));

  const build = (code: string, visited: Set<string>): HierarchyTypeNode | null => {
    if (visited.has(code)) return null;
    const t = byCode.get(code);
    if (!t) return null;
    visited.add(code);
    const children = t.allowed_child_types
      .map((c) => build(c, visited))
      .filter((n): n is HierarchyTypeNode => n !== null);
    return { id: t.id, code: t.code, label: t.label, children };
  };

  const roots = types.filter((t) => t.is_root_allowed);
  return roots
    .map((r) => build(r.code, new Set()))
    .filter((n): n is HierarchyTypeNode => n !== null);
}

export function flattenTreeForPicklist(
  nodes: HierarchyTypeNode[],
  depth = 0,
): { id: string; label: string; depth: number }[] {
  const items: { id: string; label: string; depth: number }[] = [];
  for (const node of nodes) {
    items.push({
      id: node.id,
      label: `${node.label} (${node.code})`,
      depth,
    });
    items.push(...flattenTreeForPicklist(node.children, depth + 1));
  }
  return items;
}

export function treeToNodeTypePayloads(roots: HierarchyTypeNode[]): HierarchyTypePayload[] {
  const map = new Map<string, HierarchyTypePayload>();

  const walk = (nodes: HierarchyTypeNode[], isRootLevel: boolean) => {
    for (const node of nodes) {
      const childCodes = node.children.map((c) => c.code);
      const existing = map.get(node.code);
      if (!existing) {
        map.set(node.code, {
          code: node.code,
          label: node.label,
          is_root_allowed: isRootLevel,
          allowed_child_types: childCodes,
        });
      } else {
        existing.is_root_allowed = existing.is_root_allowed || isRootLevel;
        const merged = new Set([...existing.allowed_child_types, ...childCodes]);
        existing.allowed_child_types = [...merged];
      }
      walk(node.children, false);
    }
  };

  walk(roots, true);
  return [...map.values()];
}

function addChildToTree(
  nodes: HierarchyTypeNode[],
  parentId: string | null,
  child: HierarchyTypeNode,
): HierarchyTypeNode[] {
  if (!parentId) return [...nodes, child];
  return nodes.map((node) => {
    if (node.id === parentId) {
      return { ...node, children: [...node.children, child] };
    }
    return { ...node, children: addChildToTree(node.children, parentId, child) };
  });
}

function removeFromTree(nodes: HierarchyTypeNode[], targetId: string): HierarchyTypeNode[] {
  return nodes
    .filter((n) => n.id !== targetId)
    .map((n) => ({ ...n, children: removeFromTree(n.children, targetId) }));
}

function collectCodes(nodes: HierarchyTypeNode[]): Set<string> {
  const codes = new Set<string>();
  const walk = (list: HierarchyTypeNode[]) => {
    for (const n of list) {
      codes.add(n.code);
      walk(n.children);
    }
  };
  walk(nodes);
  return codes;
}

function TypeTreePreview({
  nodes,
  depth,
  selectedParentId,
  onSelectParent,
  onAddChild,
  onRemove,
}: {
  nodes: HierarchyTypeNode[];
  depth: number;
  selectedParentId: string | null;
  onSelectParent: (id: string | null) => void;
  onAddChild: (parentId: string) => void;
  onRemove: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const toggle = (id: string) => {
    setExpanded((prev) => ({ ...prev, [id]: prev[id] === false }));
  };

  if (nodes.length === 0) {
    return (
      <p className="py-6 text-center text-sm text-muted-foreground">
        No levels yet. Add a root node to start building your tree.
      </p>
    );
  }

  return (
    <ul className={cn(depth > 0 && "ml-4 border-l border-border pl-3")}>
      {nodes.map((node) => {
        const isOpen = expanded[node.id] !== false;
        const hasChildren = node.children.length > 0;
        const isSelected = selectedParentId === node.id;

        return (
          <li key={node.id} className="py-1">
            <div
              className={cn(
                "group flex items-center gap-2 rounded-lg border px-2 py-1.5 transition-colors",
                isSelected ? "border-primary bg-primary/10" : "border-transparent hover:bg-muted/50",
              )}
            >
              <button
                type="button"
                className="shrink-0 text-muted-foreground"
                onClick={() => hasChildren && toggle(node.id)}
              >
                {hasChildren ? (
                  isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />
                ) : (
                  <span className="inline-block w-4" />
                )}
              </button>
              <button
                type="button"
                className="min-w-0 flex-1 text-left"
                onClick={() => onSelectParent(node.id)}
              >
                <span className="font-medium">{node.label}</span>
                <Badge variant="outline" className="ml-2 text-[10px]">
                  {node.code}
                </Badge>
              </button>
              <div className="flex shrink-0 gap-0.5 opacity-0 transition-opacity group-hover:opacity-100">
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7"
                  title="Add child level"
                  onClick={() => {
                    onSelectParent(node.id);
                    onAddChild(node.id);
                  }}
                >
                  <Plus className="h-3.5 w-3.5" />
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7"
                  onClick={() => onRemove(node.id)}
                >
                  <Trash2 className="h-3.5 w-3.5 text-destructive" />
                </Button>
              </div>
            </div>
            {hasChildren && isOpen && (
              <TypeTreePreview
                nodes={node.children}
                depth={depth + 1}
                selectedParentId={selectedParentId}
                onSelectParent={onSelectParent}
                onAddChild={onAddChild}
                onRemove={onRemove}
              />
            )}
          </li>
        );
      })}
    </ul>
  );
}

export function HierarchyTypeTreeBuilder({
  tree,
  onChange,
  formError,
  onFormError,
}: {
  tree: HierarchyTypeNode[];
  onChange: (tree: HierarchyTypeNode[]) => void;
  formError: string | null;
  onFormError: (msg: string | null) => void;
}) {
  const [parentId, setParentId] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [label, setLabel] = useState("");

  const picklistOptions = useMemo(() => flattenTreeForPicklist(tree), [tree]);
  const existingCodes = useMemo(() => collectCodes(tree), [tree]);

  const handleAdd = () => {
    onFormError(null);
    const normalizedCode = code.trim().toLowerCase().replace(/\s+/g, "-");
    const normalizedLabel = label.trim();

    if (!normalizedCode || !normalizedLabel) {
      onFormError("Code and label are required.");
      return;
    }
    if (!CODE_PATTERN.test(normalizedCode)) {
      onFormError("Code must be lowercase letters, numbers, and hyphens only (e.g. head-office).");
      return;
    }
    if (existingCodes.has(normalizedCode)) {
      onFormError(`Code "${normalizedCode}" already exists in the tree.`);
      return;
    }

    const newNode: HierarchyTypeNode = {
      id: newId(),
      code: normalizedCode,
      label: normalizedLabel,
      children: [],
    };

    onChange(addChildToTree(tree, parentId, newNode));
    setCode("");
    setLabel("");
    if (parentId) setParentId(parentId);
  };

  const handleRemove = (id: string) => {
    onChange(removeFromTree(tree, id));
    if (parentId === id) setParentId(null);
  };

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Add hierarchy level</CardTitle>
          <CardDescription>
            Pick a parent from the tree, then define the new child level. Relationships are built
            automatically — no comma-separated values.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="parent-picklist">Parent node</Label>
            <select
              id="parent-picklist"
              className="mt-1 flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
              value={parentId ?? ""}
              onChange={(e) => setParentId(e.target.value || null)}
            >
              <option value="">None — root level (top of tree)</option>
              {picklistOptions.map((opt) => (
                <option key={opt.id} value={opt.id}>
                  {"—".repeat(opt.depth)}
                  {opt.depth > 0 ? " " : ""}
                  {opt.label}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-muted-foreground">
              The new level will be added as a child of the selected parent.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <Label htmlFor="type-code">Code</Label>
              <Input
                id="type-code"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="head-office"
              />
            </div>
            <div>
              <Label htmlFor="type-label">Display label</Label>
              <Input
                id="type-label"
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                placeholder="Head Office"
              />
            </div>
          </div>

          {formError && <p className="text-sm text-destructive">{formError}</p>}

          <Button type="button" onClick={handleAdd} className="w-full sm:w-auto">
            <Plus className="mr-1 h-4 w-4" />
            {parentId ? "Add child level" : "Add root level"}
          </Button>
        </CardContent>
      </Card>

      <Card className="lg:sticky lg:top-4 lg:self-start">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <GitBranch className="h-4 w-4 text-primary" />
            Level tree structure
          </CardTitle>
          <CardDescription>
            Click a node to set it as parent, or use + to add a child directly.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <TypeTreePreview
            nodes={tree}
            depth={0}
            selectedParentId={parentId}
            onSelectParent={setParentId}
            onAddChild={setParentId}
            onRemove={handleRemove}
          />
        </CardContent>
      </Card>
    </div>
  );
}

export { CODE_PATTERN };
