"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface OrgContextState {
  selectedNodeId: string | null;
  setSelectedNodeId: (id: string | null) => void;
}

export const useOrgContextStore = create<OrgContextState>()(
  persist(
    (set) => ({
      selectedNodeId: null,
      setSelectedNodeId: (id) => set({ selectedNodeId: id }),
    }),
    { name: "enterpriseos-org-context" },
  ),
);
