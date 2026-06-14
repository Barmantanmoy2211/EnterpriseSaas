"use client";

import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { Input } from "@/components/ui/input";
import { searchApi } from "@/lib/api/search";
import { useAuthStore } from "@/stores/auth-store";

export function GlobalSearch() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);

  const { data, isFetching } = useQuery({
    queryKey: ["search", query],
    queryFn: () => searchApi.search(accessToken!, query),
    enabled: !!accessToken && query.length >= 2,
  });

  const entityLinks: Record<string, string> = {
    org_node: "/organization",
    user: "/settings/roles",
    employee: "/employees",
    job: "/recruitment",
    candidate: "/recruitment",
  };

  return (
    <div className="relative w-full max-w-md">
      <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        className="pl-9"
        placeholder="Search organization, users..."
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 200)}
      />
      {open && query.length >= 2 && (
        <div className="absolute left-0 right-0 top-full z-50 mt-1 rounded-xl border bg-card shadow-lg">
          {isFetching && <p className="p-3 text-sm text-muted-foreground">Searching...</p>}
          {!isFetching && data?.results.length === 0 && (
            <p className="p-3 text-sm text-muted-foreground">No results</p>
          )}
          {data?.results.map((r) => (
            <Link
              key={`${r.entity_type}-${r.entity_id}`}
              href={entityLinks[r.entity_type] ?? "/dashboard"}
              className="block border-b px-4 py-3 text-sm last:border-0 hover:bg-muted"
            >
              <p className="font-medium">{r.title}</p>
              <p className="text-xs text-muted-foreground">
                {r.entity_type} · {r.body}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
