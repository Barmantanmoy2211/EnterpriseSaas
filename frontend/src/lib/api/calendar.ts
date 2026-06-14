import { api } from "./client";

export interface CalendarEvent {
  id: string;
  title: string;
  description: string;
  start_at: string;
  end_at: string;
  organizer_id: string;
  attendee_ids: string[];
  location: string;
  all_day: boolean;
}

export const calendarApi = {
  list: (token: string) => api.get<CalendarEvent[]>("/api/v1/calendar/events", { token }),

  create: (token: string, data: Partial<CalendarEvent> & { title: string; start_at: string; end_at: string }) =>
    api.post<CalendarEvent>("/api/v1/calendar/events", data, { token }),

  delete: (token: string, id: string) => api.delete<void>(`/api/v1/calendar/events/${id}`, { token }),
};
