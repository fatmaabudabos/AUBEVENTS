import React, { useEffect, useMemo, useRef, useState } from "react";
import { api } from "../api";
import "./AdminPanel.css";

/**
 * AdminEventsPanel.jsx (frontend only)
 *
 * A lightweight React admin interface that integrates with the given JSON API:
 *  - Create: POST   /api/events
 *  - Read:   GET    /api/events/:id    (used for editing)
 *  - Update: PATCH  /api/events/:id    (send only changed fields)
 *  - Delete: DELETE /api/events/:id
 *
 * Fields handled: time, location, capacity, organizers, speakers, title, description.
 * Organizers & speakers are arrays at the API level; the UI lets you manage them as comma-separated chips.
 *
 * Notes
 * - This is FRONTEND ONLY. No backend code here. It calls the endpoints above via fetch.
 * - To plug in, ensure CORS is enabled server-side if hosted on different origins.
 * - Change API_BASE if your backend lives elsewhere.
 */

// Using shared api() helper which reads VITE_API_BASE_URL and adds Authorization when auth: true

// ----------------------
// Utilities
// ----------------------
const toArray = (val) => {
  if (!val) return [];
  if (Array.isArray(val)) return val;
  // split on commas; trim blanks; drop empties
  return String(val)
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
};

const toCSV = (arr) => (Array.isArray(arr) ? arr.join(", ") : "");

const parseCapacity = (v) => {
  if (v === "" || v === null || v === undefined) return "";
  const n = Number(v);
  if (!Number.isFinite(n)) return NaN;
  if (n < 0) return NaN;
  return Math.floor(n);
};

const isIsoLike = (s) => /\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(String(s || ""));

const toApiTime = (localInput) => {
  // <input type="datetime-local"> returns e.g. "2025-10-22T14:00"
  // API expects ISO 8601 with seconds if possible (no TZ assumed). We'll add ":00" if missing
  if (!localInput) return "";
  const base = String(localInput);
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(base)) return base + ":00";
  return base; // assume already ISO-like
};

const fromApiTimeToLocal = (apiTime) => {
  // Given "2025-10-22T14:00:00" => return "2025-10-22T14:00" to fit datetime-local
  if (!apiTime) return "";
  const s = String(apiTime);
  const m = s.match(/^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})/);
  return m ? m[1] : s;
};

async function apiJson(path, options = {}) {
  const { method = 'GET', body } = options;
  return api(path, { method, body: body ? JSON.parse(body) : undefined, auth: true });
}

// ----------------------
// Toasts
// ----------------------
function useToasts() {
  const [toasts, setToasts] = useState([]);
  const add = (variant, msg) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((t) => [...t, { id, variant, msg }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 3800);
  };
  return {
    toasts,
    success: (m) => add("success", m),
    error: (m) => add("error", m),
    info: (m) => add("info", m),
  };
}

function Toasts({ items }) {
  return (
    <div className="toast-container">
      {items.map((t) => (
        <div key={t.id} className={`toast toast-${t.variant}`}>
          {t.msg}
        </div>
      ))}
    </div>
  );
}

// ----------------------
// Form components
// ----------------------
function Labeled({ label, children, required }) {
  return (
    <label className="admin-label">
      <span className="admin-label-text">
        {label} {required && <span className="required">*</span>}
      </span>
      {children}
    </label>
  );
}

function TextInput(props) {
  return (
    <input
      {...props}
      className={`admin-input ${props.className || ""}`}
    />
  );
}

function TextArea(props) {
  return (
    <textarea
      {...props}
      className={`admin-input admin-textarea ${props.className || ""}`}
    />
  );
}

function Button({ variant = "primary", children, className = "", ...rest }) {
  return (
    <button className={`btn btn-${variant} ${className}`} {...rest}>
      {children}
    </button>
  );
}

// Track pristine vs. dirty fields for PATCH
function useDirtyTracker(initial) {
  const [values, setValues] = useState(initial);
  const initialRef = useRef(initial);
  useEffect(() => {
    setValues(initial);
    initialRef.current = initial;
  }, [initial]);

  const setField = (k, v) => setValues((s) => ({ ...s, [k]: v }));
  const resetToInitial = () => {
    setValues(initialRef.current);
  };
  const dirtyPatch = useMemo(() => {
    const out = {};
    for (const k of Object.keys(values || {})) {
      if (values[k] !== initialRef.current[k]) out[k] = values[k];
    }
    return out;
  }, [values]);

  return { values, setField, resetToInitial, dirtyPatch };
}

// ----------------------
// Event Form (Create & Edit)
// ----------------------
function EventForm({ mode, eventId, initial, onCancel, onCreated, onUpdated, toast }) {
  const defaultInitial = React.useMemo(() => ({
    title: "",
    description: "",
    time: "",
    location: "",
    capacity: "",
    organizers: "",
    speakers: "",
  }), []);
  const stableInitial = initial ?? defaultInitial;

  const { values, setField, resetToInitial, dirtyPatch } = useDirtyTracker(stableInitial);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showRetryModal, setShowRetryModal] = useState(false);
  const [lastError, setLastError] = useState("");

  // Check if form has any content
  const hasContent = useMemo(() => {
    return Object.values(values).some(value => String(value).trim() !== "");
  }, [values]);


  // Automatic loading disabled - data is passed via initial prop when Load button is pressed
  // This prevents unwanted API calls when editId changes in the input field

  const onSubmit = async (e) => {
    e.preventDefault();
    // Validate
    if (!values.title.trim()) return toast.error("Title is required");
    if (!values.time || !isIsoLike(values.time)) return toast.error("Time must be set (YYYY-MM-DDTHH:MM)");
    const cap = parseCapacity(values.capacity);
    if (Number.isNaN(cap)) return toast.error("Capacity must be a non-negative integer");

    setIsSubmitting(true);

    // Prepare payload
    const payload = {
      title: values.title.trim(),
      description: values.description.trim(),
      time: toApiTime(values.time),
      location: values.location.trim(),
      capacity: cap === "" ? 0 : cap,
      organizers: toArray(values.organizers),
      speakers: toArray(values.speakers),
    };

    try {
      if (mode === "create") {
        const res = await apiJson(`/api/events`, { method: "POST", body: JSON.stringify(payload) });
        toast.success(res?.message || "Event created successfully");
        onCreated?.(res); // This will force form remount via formResetKey
      } else {
        // For PATCH, send only changed fields
        const patch = {};
        const diff = dirtyPatch;
        // Map field names to API names and transform
        if (diff.title !== undefined) patch.title = diff.title.trim();
        if (diff.description !== undefined) patch.description = diff.description.trim();
        if (diff.time !== undefined) patch.time = toApiTime(diff.time);
        if (diff.location !== undefined) patch.location = diff.location.trim();
        if (diff.capacity !== undefined) {
          const c = parseCapacity(diff.capacity);
          if (Number.isNaN(c)) return toast.error("Capacity must be a non-negative integer");
          patch.capacity = c === "" ? 0 : c;
        }
        if (diff.organizers !== undefined) patch.organizers = toArray(diff.organizers);
        if (diff.speakers !== undefined) patch.speakers = toArray(diff.speakers);

        if (!Object.keys(patch).length) {
          setIsSubmitting(false);
          toast.info("No changes to save");
          return;
        }
        const res = await apiJson(`/api/events/${eventId}`, { method: "PATCH", body: JSON.stringify(patch) });
        toast.success(res?.message || "Event updated successfully");
        onUpdated?.(res); // This will force form remount via formResetKey
      }
    } catch (e) {
      setLastError(e.message || "Request failed");
      setShowRetryModal(true);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={onSubmit} className="event-form">
      <div className="form-grid">
        <Labeled label="Title" required>
          <TextInput
            placeholder="e.g., AUB Career Fair 2025"
            value={values.title}
            onChange={(e) => setField("title", e.target.value)}
          />
        </Labeled>
        <Labeled label="Time (local)" required>
          <TextInput
            type="datetime-local"
            value={values.time}
            onChange={(e) => setField("time", e.target.value)}
          />
        </Labeled>
        <Labeled label="Location">
          <TextInput
            placeholder="West Hall, Auditorium B"
            value={values.location}
            onChange={(e) => setField("location", e.target.value)}
          />
        </Labeled>
        <Labeled label="Capacity">
          <TextInput
            type="number"
            min={0}
            step={1}
            placeholder="e.g., 120"
            value={values.capacity}
            onChange={(e) => setField("capacity", e.target.value)}
          />
        </Labeled>
      </div>
      <Labeled label="Organizers (comma-separated)">
        <TextInput
          placeholder="e.g., CCECS, AUB Alumni Club"
          value={values.organizers}
          onChange={(e) => setField("organizers", e.target.value)}
        />
      </Labeled>
      <Labeled label="Speakers (comma-separated)">
        <TextInput
          placeholder="e.g., Dr. X, Dr. Y"
          value={values.speakers}
          onChange={(e) => setField("speakers", e.target.value)}
        />
      </Labeled>
      <Labeled label="Description">
        <TextArea
          placeholder="Short description of the event..."
          value={values.description}
          onChange={(e) => setField("description", e.target.value)}
        />
      </Labeled>

      <div className="form-actions">
        <Button type="submit" variant="primary" disabled={isSubmitting}>
          {isSubmitting
            ? (mode === "create" ? "🔄 Creating..." : "🔄 Saving...")
            : (mode === "create" ? "🎉 Create Event" : "💾 Save Changes")
          }
        </Button>
        {onCancel && (
          <Button type="button" variant="secondary" onClick={() => {
            if (mode === "create" && hasContent) {
              // Clear all form fields in create mode
              resetToInitial();
            } else {
              // Regular cancel behavior (for edit mode or when no content)
              onCancel();
            }
          }} disabled={isSubmitting || !hasContent}>
            ❌ Cancel
          </Button>
        )}
      </div>

      {/* Retry Modal */}
      {showRetryModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <h3 className="modal-title">❌ {mode === "create" ? "Create Failed" : "Save Failed"}</h3>
            <p className="modal-desc">{lastError}</p>
            <div className="modal-actions">
              <Button variant="secondary" onClick={() => setShowRetryModal(false)}>
                Keep Form
              </Button>
              <Button variant="primary" onClick={() => {
                resetToInitial();
                setShowRetryModal(false);
                toast.info("Form cleared. Try again!");
              }}>
                Clear Form
              </Button>
            </div>
          </div>
        </div>
      )}
    </form>
  );
}

// ----------------------
// Delete Confirmation Modal (simple inline)
// ----------------------
function Confirm({ open, title, description, onConfirm, onCancel }) {
  if (!open) return null;
  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <h3 className="modal-title">{title}</h3>
        <p className="modal-desc">{description}</p>
        <div className="modal-actions">
          <Button variant="secondary" onClick={onCancel}>Cancel</Button>
          <Button variant="danger" onClick={onConfirm}>Delete</Button>
        </div>
      </div>
    </div>
  );
}

// ----------------------
// Admin Shell
// ----------------------
export default function AdminEventsPanel() {
  const toast = useToasts();

  // Local cache of events created/edited during this session (because no list endpoint was specified).
  // You can remove this if you later implement GET /api/events for listing.
  const [localEvents, setLocalEvents] = useState([]);
  const [serverEvents, setServerEvents] = useState([]);

  // UI state
  const [mode, setMode] = useState("create"); // "create" | "edit"
  const [editId, setEditId] = useState("");
  const [showConfirm, setShowConfirm] = useState(false);
  const [formResetKey, setFormResetKey] = useState(0); // Force form remount
  const [loadedEvent, setLoadedEvent] = useState(null); // Event data loaded via Load button
  const [showAllServerEvents, setShowAllServerEvents] = useState(false); // Show/hide all server events

  // Auto-refresh events when admin panel loads
  useEffect(() => {
    refreshServerEvents();
  }, []); // Run once on mount

  const selected = useMemo(() => {
    // Look in both local and server events for the selected event
    const local = localEvents.find((e) => String(e.id) === String(editId));
    const server = serverEvents.find((e) => String(e.id) === String(editId));
    return local || server;
  }, [localEvents, serverEvents, editId]);

  // Simulate pressing the refresh button
  const refreshServerEvents = async () => {
    try {
      const res = await apiJson(`/api/events`, { method: "GET" });
      setServerEvents(res?.events || []);
    } catch (e) {
      // Silently fail - user can manually refresh if needed
    }
  };

  const handleCreated = (res) => {
    // If backend returns the new event id, keep it; else synthesize a local id.
    const newId = res?.id ?? Math.random().toString(36).slice(2);
    setLocalEvents((evs) => [
      {
        id: newId,
        title: res?.title ?? "",
        time: res?.time ?? "",
        location: res?.location ?? "",
        capacity: res?.capacity ?? 0,
        organizers: res?.organizers ?? [],
        speakers: res?.speakers ?? [],
        description: res?.description ?? "",
      },
      ...evs,
    ]);
    // Clear loaded event data and force immediate form remount to clear all fields
    setLoadedEvent(null);
    setFormResetKey(k => k + 1);
    // Simulate refresh button press
    refreshServerEvents();
  };

  const handleUpdated = async (res) => {
    const id = res?.id ?? editId;
    // After saving changes in edit mode, return to create mode with an empty form
    setMode("create");
    setEditId("");
    setLoadedEvent(null); // Clear loaded event data
    // Force immediate form remount to clear all fields instantly
    setFormResetKey(k => k + 1);
    // Simulate refresh button press
    refreshServerEvents();

    // Update local cache in background (non-blocking)
    try {
      const fresh = await apiJson(`/api/events/${id}`, { method: "GET" });
      setLocalEvents((evs) => {
        const idx = evs.findIndex((x) => String(x.id) === String(id));
        if (idx === -1) return evs;
        const copy = evs.slice();
        copy[idx] = { id, ...fresh };
        return copy;
      });
    } catch {
      // Fallback: leave local as-is
    }
  };

  const doDelete = async () => {
    try {
      if (!editId) return;
      await apiJson(`/api/events/${editId}`, { method: "DELETE" });
      toast.success("Event deleted successfully");
      setLocalEvents((evs) => evs.filter((e) => String(e.id) !== String(editId)));
      setShowConfirm(false);
      setEditId("");
      setMode("create");
      // Refresh server events after deletion
      refreshServerEvents();
    } catch (e) {
      toast.error(e.message || "Delete failed");
    }
  };

  const loadForEdit = async () => {
    if (!editId) return toast.error("Enter an event ID to load");
    try {
      const data = await apiJson(`/api/events/${editId}`, { method: "GET" });
      // Store the loaded event data - this will be used by the form
      setLoadedEvent(data);
      setMode("edit");
      // Force form remount with new data
      setFormResetKey(k => k + 1);
      toast.success(`Loaded event ${editId} for editing`);
    } catch (e) {
      toast.error(e.message || "Failed to load event");
    }
  };

  const editEventFromList = async (eventId, eventData = null) => {
    setEditId(String(eventId));

    if (eventData) {
      // Use the provided event data directly (for local events)
      setLoadedEvent(eventData);
      setMode("edit");
      setFormResetKey(k => k + 1);
    } else {
      // Fetch from server (for server events)
      try {
        const data = await apiJson(`/api/events/${eventId}`, { method: "GET" });
        setLoadedEvent(data);
        setMode("edit");
        setFormResetKey(k => k + 1);
      } catch (e) {
        toast.error(e.message || "Failed to load event");
      }
    }

    // Scroll to top of page to show the form
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="admin-theme">
      {/* Header */}
      <div className="admin-header">
        <div className="admin-header-inner">
          <div className="brand">
            <div className="brand-logo">A</div>
            <div className="brand-title">AUB EVENTS</div>
            <div className="admin-badge">Admin Panel</div>
          </div>
          <div className="header-actions">
            <Button variant="secondary" onClick={() => window.location.assign('/dashboard')}>
              👤 Student View
            </Button>
          </div>
        </div>
      </div>

      <div className="admin-container">
        <div className="admin-grid">
          {/* Main form */}
          <div className="admin-card">
            <div className="card-top">
              <h2 className="section-title">
                {mode === "create" ? "🎉 Create New Event" :
                  `✏️ Edit Event #${loadedEvent?.id || 'Loading...'}`}
              </h2>
              {mode === "edit" && (
                <div className="card-actions">
                  <Button variant="secondary" onClick={() => { setMode("create"); setEditId(""); setLoadedEvent(null); }}>
                    ➕ New Event
                  </Button>
                  <Button variant="danger" onClick={() => setShowConfirm(true)}>🗑️ Delete</Button>
                </div>
              )}
            </div>
            <div className="card-body">
              <EventForm
                key={`${mode}-${loadedEvent?.id || editId || 'new'}-${formResetKey}`}
                mode={mode}
                eventId={loadedEvent?.id || editId}
                initial={mode === "edit" && loadedEvent ? {
                  title: loadedEvent.title || "",
                  description: loadedEvent.description || "",
                  time: fromApiTimeToLocal(loadedEvent.time || ""),
                  location: loadedEvent.location || "",
                  capacity: String(loadedEvent.capacity ?? ""),
                  organizers: toCSV(loadedEvent.organizers || []),
                  speakers: toCSV(loadedEvent.speakers || [])
                } : undefined}
                onCreated={handleCreated}
                onUpdated={handleUpdated}
                onCancel={() => { setMode("create"); setEditId(""); setLoadedEvent(null); }}
                toast={toast}
              />
            </div>
          </div>

          {/* Tools sidebar */}
          <div className="admin-card">
            <h3 className="section-title">🔧 Quick Tools</h3>
            <div className="tools">
              <div className="tools-row">
                <TextInput
                  placeholder="Enter Event ID"
                  value={editId}
                  onChange={(e) => setEditId(e.target.value)}
                />
                <Button variant="secondary" onClick={loadForEdit}>📂 Load</Button>
              </div>
              <p className="muted">
                Enter an event ID to edit existing events
                {/* <span className="code">GET /api/events/:id</span> */}
              </p>
              <div className="tools-actions">
                <Button variant="secondary" onClick={async () => {
                  try {
                    const res = await apiJson(`/api/events`, { method: "GET" });
                    setServerEvents(res?.events || []);
                    toast.success(`📊 Loaded ${res?.events?.length ?? 0} events from server`);
                  } catch (e) {
                    toast.error(e.message || "Failed to load events");
                  }
                }}>🔄 Refresh Events</Button>
              </div>
            </div>

            <div className="server-list">
              <h4 className="subhead">📝 Recent Events</h4>
              <p className="muted">Events created this session</p>
              <div className="list">
                {localEvents.length === 0 ? (
                  <div className="muted">No events created yet. Start by creating your first event! 🎉</div>
                ) : (
                  <ul className="list-items">
                    {localEvents.map((e) => (
                      <li key={e.id} className="list-item">
                        <div className="list-item-main">
                          <div className="item-title">#{String(e.id)} – {e.title || "Untitled Event"}</div>
                          <div className="item-sub">📍 {e.location} • 📅 {fromApiTimeToLocal(e.time)}</div>
                        </div>
                        <div className="list-item-actions">
                          <Button variant="secondary" onClick={() => editEventFromList(e.id, e)}>✏️ Edit</Button>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              <div className="server-list">
                <h4 className="subhead">🌐 All Events</h4>
                <p className="muted">All your events</p>
                <div className="list">
                  {serverEvents.length === 0 ? (
                    <div className="muted">Click "🔄 Refresh Events" to load all your events</div>
                  ) : (
                    <>
                      <ul className="list-items">
                        {(showAllServerEvents ? serverEvents : serverEvents.slice(0, 5)).map((e) => (
                          <li key={e.id} className="list-item">
                            <div className="list-item-main">
                              <div className="item-title">#{String(e.id)} – {e.title || "Untitled Event"}</div>
                              <div className="item-sub">📍 {e.location} • 📅 {fromApiTimeToLocal(e.time)}</div>
                            </div>
                            <div className="list-item-actions">
                              <Button variant="secondary" onClick={() => editEventFromList(e.id)}>✏️ Edit</Button>
                            </div>
                          </li>
                        ))}
                      </ul>
                      {serverEvents.length > 5 && (
                        <div className="show-more-section">
                          <Button
                            variant="secondary"
                            onClick={() => setShowAllServerEvents(!showAllServerEvents)}
                            className="show-more-btn"
                          >
                            {showAllServerEvents ? '📈 Show Less' : `📋 Show More (${serverEvents.length - 5} more)`}
                          </Button>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Toasts items={toast.toasts} />
      <Confirm
        open={showConfirm}
        title={`Delete event #${editId}?`}
        description="This action cannot be undone."
        onConfirm={doDelete}
        onCancel={() => setShowConfirm(false)}
      />
    </div>
  );
}
