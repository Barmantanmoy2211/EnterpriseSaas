"use client";

import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useDraggable,
  useDroppable,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { CSS } from "@dnd-kit/utilities";
import { ChevronDown, ChevronRight, GripVertical, Pencil, Plus, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { OrgNode, OrgNodeType } from "@/lib/api/organization";
import { cn } from "@/lib/utils";

const ROOT_DROP_ID = "org-root-drop";

function findNode(tree: OrgNode[], id: string): OrgNode | null {
  for (const node of tree) {
    if (node.id === id) return node;
    const found = findNode(node.children, id);
    if (found) return found;
  }
  return null;
}

function collectDescendantIds(node: OrgNode): Set<string> {
  const ids = new Set<string>();
  const walk = (n: OrgNode) => {
    ids.add(n.id);
    n.children.forEach(walk);
  };
  walk(node);
  return ids;
}

function TreeNodeRow({
  node,
  nodeTypes,
  depth,
  canEdit,
  activeDragId,
  onAddChild,
  onDelete,
  onRename,
}: {
  node: OrgNode;
  nodeTypes: OrgNodeType[];
  depth: number;
  canEdit: boolean;
  activeDragId: string | null;
  onAddChild: (parent: OrgNode, name: string, type: string) => void;
  onDelete: (node: OrgNode) => void;
  onRename: (node: OrgNode, name: string) => void;
}) {
  const [expanded, setExpanded] = useState(true);
  const [adding, setAdding] = useState(false);
  const [editing, setEditing] = useState(false);
  const [childName, setChildName] = useState("");
  const [childType, setChildType] = useState("");
  const [editName, setEditName] = useState(node.name);

  const parentType = nodeTypes.find((t) => t.code === node.node_type);
  const allowedChildren = parentType?.allowed_child_types ?? [];
  const typeLabel = nodeTypes.find((t) => t.code === node.node_type)?.label ?? node.node_type;

  const { attributes, listeners, setNodeRef: setDragRef, transform, isDragging } = useDraggable({
    id: node.id,
    disabled: !canEdit,
  });

  const { setNodeRef: setDropRef, isOver } = useDroppable({
    id: `drop-${node.id}`,
    disabled: !canEdit || activeDragId === node.id,
  });

  const style = transform
    ? { transform: CSS.Translate.toString(transform), opacity: isDragging ? 0.4 : 1 }
    : undefined;

  const setRefs = (el: HTMLDivElement | null) => {
    setDragRef(el);
    setDropRef(el);
  };

  return (
    <div className="select-none">
      <div
        ref={setRefs}
        style={style}
        className={cn(
          "group flex items-center gap-2 rounded-lg border border-transparent px-2 py-1.5 transition-colors",
          isOver && "border-primary bg-primary/10",
          isDragging && "opacity-50",
        )}
      >
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className="shrink-0 text-muted-foreground hover:text-foreground"
        >
          {node.children.length > 0 ? (
            expanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />
          ) : (
            <span className="inline-block w-4" />
          )}
        </button>

        {canEdit && (
          <button
            type="button"
            className="cursor-grab text-muted-foreground hover:text-foreground active:cursor-grabbing"
            {...listeners}
            {...attributes}
            aria-label="Drag to move"
          >
            <GripVertical className="h-4 w-4" />
          </button>
        )}

        {editing ? (
          <Input
            className="h-8 max-w-[200px]"
            value={editName}
            onChange={(e) => setEditName(e.target.value)}
            onBlur={() => {
              if (editName.trim() && editName !== node.name) onRename(node, editName.trim());
              setEditing(false);
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                if (editName.trim() && editName !== node.name) onRename(node, editName.trim());
                setEditing(false);
              }
            }}
            autoFocus
          />
        ) : (
          <span className="font-medium">{node.name}</span>
        )}

        <Badge variant="secondary" className="text-xs">
          {typeLabel}
        </Badge>

        {canEdit && (
          <div className="ml-auto flex items-center gap-0.5 opacity-0 transition-opacity group-hover:opacity-100">
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setEditing(true)}>
              <Pencil className="h-3.5 w-3.5" />
            </Button>
            {allowedChildren.length > 0 && (
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setAdding(!adding)}>
                <Plus className="h-3.5 w-3.5" />
              </Button>
            )}
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              disabled={node.children.length > 0}
              onClick={() => onDelete(node)}
            >
              <Trash2 className="h-3.5 w-3.5 text-destructive" />
            </Button>
          </div>
        )}
      </div>

      {adding && canEdit && (
        <div
          className="mb-2 ml-10 flex flex-wrap items-end gap-2 rounded-lg border bg-muted/40 p-3"
          style={{ marginLeft: `${depth * 16 + 40}px` }}
        >
          <div>
            <Label className="text-xs">Name</Label>
            <Input value={childName} onChange={(e) => setChildName(e.target.value)} className="h-8" />
          </div>
          <div>
            <Label className="text-xs">Type</Label>
            <select
              className="flex h-8 rounded-md border border-input bg-background px-2 text-sm"
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
            disabled={!childName || !childType}
            onClick={() => {
              onAddChild(node, childName, childType);
              setAdding(false);
              setChildName("");
              setChildType("");
              setExpanded(true);
            }}
          >
            Add child
          </Button>
        </div>
      )}

      {expanded && node.children.length > 0 && (
        <div style={{ marginLeft: `${depth * 16 + 24}px` }} className="border-l border-border pl-2">
          {node.children.map((child) => (
            <TreeNodeRow
              key={child.id}
              node={child}
              nodeTypes={nodeTypes}
              depth={depth + 1}
              canEdit={canEdit}
              activeDragId={activeDragId}
              onAddChild={onAddChild}
              onDelete={onDelete}
              onRename={onRename}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function RootDropZone({ canEdit, isOver }: { canEdit: boolean; isOver: boolean }) {
  const { setNodeRef, isOver: over } = useDroppable({ id: ROOT_DROP_ID, disabled: !canEdit });
  const active = isOver || over;
  if (!canEdit) return null;
  return (
    <div
      ref={setNodeRef}
      className={cn(
        "mb-3 rounded-lg border-2 border-dashed px-4 py-3 text-center text-sm text-muted-foreground",
        active && "border-primary bg-primary/10 text-primary",
      )}
    >
      Drop here to move node to root level
    </div>
  );
}

export function OrgHierarchyTree({
  tree,
  nodeTypes,
  canEdit,
  onMove,
  onAddChild,
  onDelete,
  onRename,
}: {
  tree: OrgNode[];
  nodeTypes: OrgNodeType[];
  canEdit: boolean;
  onMove: (nodeId: string, parentId: string | null) => void;
  onAddChild: (parent: OrgNode | null, name: string, type: string) => void;
  onDelete: (node: OrgNode) => void;
  onRename: (node: OrgNode, name: string) => void;
}) {
  const [activeId, setActiveId] = useState<string | null>(null);
  const [rootOver, setRootOver] = useState(false);

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 8 } }));

  const activeNode = useMemo(
    () => (activeId ? findNode(tree, activeId) : null),
    [activeId, tree],
  );

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(String(event.active.id));
  };

  const handleDragEnd = (event: DragEndEvent) => {
    setActiveId(null);
    setRootOver(false);
    const { active, over } = event;
    if (!over || !canEdit) return;

    const draggedId = String(active.id);
    const overId = String(over.id);

    if (overId === ROOT_DROP_ID) {
      onMove(draggedId, null);
      return;
    }

    if (overId.startsWith("drop-")) {
      const targetId = overId.replace("drop-", "");
      if (draggedId === targetId) return;

      const dragged = findNode(tree, draggedId);
      const target = findNode(tree, targetId);
      if (!dragged || !target) return;

      const descendants = collectDescendantIds(dragged);
      if (descendants.has(targetId)) return;

      onMove(draggedId, targetId);
    }
  };

  return (
    <DndContext
      sensors={sensors}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragOver={(e) => setRootOver(e.over?.id === ROOT_DROP_ID)}
    >
      <RootDropZone canEdit={canEdit} isOver={rootOver} />

      {tree.length === 0 ? (
        <p className="py-8 text-center text-sm text-muted-foreground">
          No nodes yet. Create a root organization below.
        </p>
      ) : (
        tree.map((node) => (
          <TreeNodeRow
            key={node.id}
            node={node}
            nodeTypes={nodeTypes}
            depth={0}
            canEdit={canEdit}
            activeDragId={activeId}
            onAddChild={(parent, name, type) => onAddChild(parent, name, type)}
            onDelete={onDelete}
            onRename={onRename}
          />
        ))
      )}

      <DragOverlay>
        {activeNode ? (
          <div className="rounded-lg border bg-card px-3 py-2 shadow-lg">
            <span className="font-medium">{activeNode.name}</span>
            <Badge variant="secondary" className="ml-2 text-xs">
              {activeNode.node_type}
            </Badge>
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  );
}
