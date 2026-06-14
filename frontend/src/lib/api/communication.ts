import { api } from "./client";

export interface Message {
  id: string;
  message_type: string;
  subject: string;
  body: string;
  sender_id: string;
  recipient_id: string | null;
  channel: string;
  is_pinned: boolean;
  read_by: string[];
  created_at: string;
}

export const communicationApi = {
  list: (token: string, message_type?: string) =>
    api.get<Message[]>(
      `/api/v1/communication/messages${message_type ? `?message_type=${message_type}` : ""}`,
      { token },
    ),

  create: (token: string, data: { subject: string; body: string; message_type?: string; channel?: string }) =>
    api.post<Message>("/api/v1/communication/messages", data, { token }),

  markRead: (token: string, id: string) =>
    api.post<Message>(`/api/v1/communication/messages/${id}/read`, {}, { token }),
};
