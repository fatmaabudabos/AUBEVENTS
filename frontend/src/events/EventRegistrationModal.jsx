import React, { useState } from "react";
import { api } from "../api";
import "./Events.css";

export default function EventRegistrationModal({ event, onClose }) {
  const [form, setForm] = useState({ name: "", phone: "", notes: "" });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      await api(`/events/${event.id}/register/`, {
        method: "POST",
        body: form,
        auth: true,
      });
      setMessage("Registration successful! You’ll receive an email confirmation soon.");
    } catch (err) {
      setMessage(err.message || "Registration failed. Try again later.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>Register for {event.title}</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            name="name"
            placeholder="Full Name"
            value={form.name}
            onChange={handleChange}
            required
          />
          <input
            type="tel"
            name="phone"
            placeholder="Phone Number"
            value={form.phone}
            onChange={handleChange}
            required
          />
          <textarea
            name="notes"
            placeholder="Additional notes (optional)"
            value={form.notes}
            onChange={handleChange}
            rows="3"
          ></textarea>
          <div className="modal-actions">
            <button type="submit" disabled={loading}>
              {loading ? "Registering..." : "Confirm Registration"}
            </button>
            <button type="button" className="secondary-btn" onClick={onClose}>
              Cancel
            </button>
          </div>
        </form>
        {message && <p className="flash">{message}</p>}
      </div>
    </div>
  );
}
