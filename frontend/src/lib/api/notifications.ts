import { api } from "./client";

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  body: string;
  notification_type: string;
  is_read: boolean;
  link: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface NotificationListResponse {
  items: Notification[];
  unread_count: number;
}

export const notificationsApi = {
  list: (token: string, unreadOnly = false) =>
    api.get<NotificationListResponse>(
      `/api/v1/notifications?unread_only=${unreadOnly}`,
      { token },
    ),

  markRead: (token: string, id: string) =>
    api.patch<Notification>(`/api/v1/notifications/${id}/read`, undefined, { token }),

  markAllRead: (token: string) =>
    api.post<void>("/api/v1/notifications/read-all", undefined, { token }),
};
