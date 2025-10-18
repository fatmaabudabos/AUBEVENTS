import React from "react";

export default function EventCard({ event, onRegister }) {
  return (
    <div className="event-card">
      <h3>{event.title}</h3>
      <p className="event-date">
        {new Date(event.time).toLocaleString("en-US", {
          weekday: "short",
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        })}
      </p>
      <p className="event-location">{event.location}</p>
      <p className="event-description">{event.description}</p>
      <button className="register-btn" onClick={onRegister}>
        Register
      </button>
    </div>
  );
}
