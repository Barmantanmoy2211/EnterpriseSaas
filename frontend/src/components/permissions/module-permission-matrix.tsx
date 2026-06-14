"use client";

import type { Permission } from "@/lib/api/permissions";
import {
  ACTION_LABELS,
  MODULE_ACTIONS,
  PERMISSION_MODULES,
  SPECIAL_PERMISSIONS,
  permissionKey,
  type ModuleAction,
} from "@/config/permission-modules";
import { cn } from "@/lib/utils";

function buildPermIndex(permissions: Permission[]) {
  const byKey = new Map<string, string>();
  for (const p of permissions) {
    byKey.set(permissionKey(p.resource, p.action), p.id);
  }
  return byKey;
}

export function ModulePermissionMatrix({
  permissions,
  selectedIds,
  onChange,
  disabled,
}: {
  permissions: Permission[];
  selectedIds: string[];
  onChange: (ids: string[]) => void;
  disabled?: boolean;
}) {
  const permIndex = buildPermIndex(permissions);
  const selected = new Set(selectedIds);

  const isChecked = (resource: string, action: ModuleAction) => {
    const id = permIndex.get(permissionKey(resource, action));
    return id ? selected.has(id) : false;
  };

  const toggle = (resource: string, action: ModuleAction) => {
    const id = permIndex.get(permissionKey(resource, action));
    if (!id) return;
    const next = new Set(selectedIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    onChange([...next]);
  };

  const toggleRow = (resource: string, on: boolean) => {
    const next = new Set(selectedIds);
    for (const action of MODULE_ACTIONS) {
      const id = permIndex.get(permissionKey(resource, action));
      if (!id) continue;
      if (on) next.add(id);
      else next.delete(id);
    }
    onChange([...next]);
  };

  const toggleSpecial = (resource: string, action: string) => {
    const id = permIndex.get(permissionKey(resource, action));
    if (!id) return;
    const next = new Set(selectedIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    onChange([...next]);
  };

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full min-w-[520px] text-sm">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="px-3 py-2 text-left font-medium">Module</th>
              {MODULE_ACTIONS.map((action) => (
                <th key={action} className="px-3 py-2 text-center font-medium">
                  {ACTION_LABELS[action]}
                </th>
              ))}
              <th className="px-3 py-2 text-center font-medium">All</th>
            </tr>
          </thead>
          <tbody>
            {PERMISSION_MODULES.map((mod) => {
              const rowAll = MODULE_ACTIONS.every((a) => isChecked(mod.code, a));
              const rowSome = MODULE_ACTIONS.some((a) => isChecked(mod.code, a));
              return (
                <tr key={mod.code} className="border-b last:border-0">
                  <td className="px-3 py-2 font-medium">{mod.label}</td>
                  {MODULE_ACTIONS.map((action) => (
                    <td key={action} className="px-3 py-2 text-center">
                      <input
                        type="checkbox"
                        disabled={disabled || !permIndex.has(permissionKey(mod.code, action))}
                        checked={isChecked(mod.code, action)}
                        onChange={() => toggle(mod.code, action)}
                        className="h-4 w-4 rounded border-input"
                        aria-label={`${mod.label} ${ACTION_LABELS[action]}`}
                      />
                    </td>
                  ))}
                  <td className="px-3 py-2 text-center">
                    <input
                      type="checkbox"
                      disabled={disabled}
                      checked={rowAll}
                      ref={(el) => {
                        if (el) el.indeterminate = rowSome && !rowAll;
                      }}
                      onChange={() => toggleRow(mod.code, !rowAll)}
                      className="h-4 w-4 rounded border-input"
                      aria-label={`${mod.label} all permissions`}
                    />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div>
        <p className="mb-2 text-xs font-medium text-muted-foreground">Additional permissions</p>
        <div className="grid gap-2 sm:grid-cols-2">
          {SPECIAL_PERMISSIONS.map((sp) => {
            const id = permIndex.get(permissionKey(sp.resource, sp.action));
            if (!id) return null;
            return (
              <label
                key={permissionKey(sp.resource, sp.action)}
                className={cn(
                  "flex cursor-pointer items-center gap-2 rounded-md border p-2 text-sm",
                  disabled && "opacity-60",
                )}
              >
                <input
                  type="checkbox"
                  disabled={disabled}
                  checked={selected.has(id)}
                  onChange={() => toggleSpecial(sp.resource, sp.action)}
                />
                <span>{sp.label}</span>
              </label>
            );
          })}
        </div>
      </div>
    </div>
  );
}
