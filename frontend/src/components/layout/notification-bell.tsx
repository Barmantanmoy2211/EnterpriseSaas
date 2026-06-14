"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bell, Check } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { notificationsApi } from "@/lib/api/notifications";
import { useAuthStore } from "@/stores/auth-store";

export function NotificationBell() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const [open, setOpen] = useState(false);
  const queryClient = useQueryClient();

  const { data } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => notificationsApi.list(accessToken!, false),
    enabled: !!accessToken,
    refetchInterval: 30000,
  });

  const markAll = useMutation({
    mutationFn: () => notificationsApi.markAllRead(accessToken!),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });

  const unread = data?.unread_count ?? 0;

  return (
    <div className="relative">
      <Button variant="ghost" size="icon" onClick={() => setOpen(!open)} aria-label="Notifications">
        <Bell className="h-5 w-5" />
        {unread > 0 && (
          <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[10px] text-primary-foreground">
            {unread > 9 ? "9+" : unread}
          </span>
        )}
      </Button>

      {open && (
        <div className="absolute right-0 top-full z-50 mt-2 w-80 rounded-xl border bg-card shadow-lg">
          <div className="flex items-center justify-between border-b px-4 py-3">
            <span className="font-semibold">Notifications</span>
            {unread > 0 && (
              <Button variant="ghost" size="sm" onClick={() => markAll.mutate()}>
                <Check className="mr-1 h-3 w-3" />
                Mark all read
              </Button>
            )}
          </div>
          <div className="max-h-80 overflow-auto">
            {data?.items.length === 0 && (
              <p className="p-4 text-sm text-muted-foreground">No notifications</p>
            )}
            {data?.items.map((n) => (
              <div
                key={n.id}
                className={`border-b px-4 py-3 text-sm last:border-0 ${!n.is_read ? "bg-accent/50" : ""}`}
              >
                {n.link ? (
                  <Link href={n.link} className="font-medium hover:underline" onClick={() => setOpen(false)}>
                    {n.title}
                  </Link>
                ) : (
                  <p className="font-medium">{n.title}</p>
                )}
                <p className="text-muted-foreground">{n.body}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
