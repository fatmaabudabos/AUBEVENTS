import React, { useEffect, useState } from "react";
import "./Events.css";
import { api } from "../api";
import EventCard from "./EventCard";
import EventRegistrationModal from "./EventRegistrationModal";

export default function EventsPage() {
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        // ✅ use /api prefix so Vite proxy forwards to Django
        const data = await api("/api/events/", { method: "GET", auth: true });
        // handle either an array or a wrapped object like {items:[...]} or {results:[...]}
        const list =
          Array.isArray(data) ? data :
          data?.items ?? data?.results ?? [];
        setEvents(list);
      } catch (err) {
        setError("Failed to load events. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    fetchEvents();
  }, []);

  if (loading) return <div className="events-loading">Loading events…</div>;
  if (error) return <div className="flash err">{error}</div>;

  return (
    <div className="events-page">
      <h1 className="events-title">Upcoming Events</h1>
      {events.length === 0 && (
        <p className="no-events">No events available right now.</p>
      )}
      <div className="events-grid">
        {events.map((ev) => (
          <EventCard
            key={ev.id}
            event={ev}
            onRegister={() => setSelectedEvent(ev)}
          />
        ))}
      </div>
      {selectedEvent && (
        <EventRegistrationModal
          event={selectedEvent}
          onClose={() => setSelectedEvent(null)}
        />
      )}
    </div>
  );
}
