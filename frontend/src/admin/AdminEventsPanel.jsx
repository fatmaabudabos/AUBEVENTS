import React, { useEffect, useMemo, useRef, useState } from "react";

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

const API_BASE = typeof process !== "undefined" && process.env?.REACT_APP_API_BASE
  ? process.env.REACT_APP_API_BASE
  : ""; // e.g., "http://localhost:5000". Left blank to use same origin.

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
  const res = await fetch(API_BASE + path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    credentials: "include",
    ...options,
  });
  const text = await res.text();
  let payload = null;
  try {
    payload = text ? JSON.parse(text) : null;
  } catch (_) {
    payload = null;
  }
  if (!res.ok) {
    const msg = payload?.error || `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return payload;
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
    <div className="fixed top-4 right-4 z-50 grid gap-2">
      {items.map((t) => (
        <div
          key={t.id}
          className={`rounded-2xl shadow-lg px-4 py-3 text-sm ${
            t.variant === "success"
              ? "bg-green-100 text-green-800 border border-green-300"
              : t.variant === "error"
              ? "bg-red-100 text-red-800 border border-red-300"
              : "bg-slate-100 text-slate-800 border border-slate-300"
          }`}
        >
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
    <label className="grid gap-1">
      <span className="text-sm font-semibold text-slate-700">
        {label} {required && <span className="text-red-600">*</span>}
      </span>
      {children}
    </label>
  );
}

function TextInput(props) {
  return (
    <input
      {...props}
      className={
        "w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-rose-300 " +
        (props.className || "")
      }
    />
  );
}

function TextArea(props) {
  return (
    <textarea
      {...props}
      className={
        "w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-rose-300 min-h-[88px] " +
        (props.className || "")
      }
    />
  );
}

function Button({ variant = "primary", children, className = "", ...rest }) {
  const base = "rounded-xl px-4 py-2 text-sm font-semibold shadow-sm disabled:opacity-60 disabled:cursor-not-allowed";
  const map = {
    primary: "bg-rose-700 text-white hover:bg-rose-800",
    secondary: "bg-white text-slate-800 border border-slate-300 hover:bg-slate-50",
    danger: "bg-red-600 text-white hover:bg-red-700",
  };
  return (
    <button className={`${base} ${map[variant]} ${className}`} {...rest}>
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
  const dirtyPatch = useMemo(() => {
    const out = {};
    for (const k of Object.keys(values || {})) {
      if (values[k] !== initialRef.current[k]) out[k] = values[k];
    }
    return out;
  }, [values]);

  return { values, setField, dirtyPatch };
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

  const { values, setField, dirtyPatch } = useDirtyTracker(stableInitial);


  // If editing and no initial provided, fetch once by id
  useEffect(() => {
    let ignore = false;
    async function load() {
      if (mode !== "edit" || !eventId || initial) return;
      try {
        const data = await apiJson(`/api/events/${eventId}`, { method: "GET" });
        if (ignore) return;
        setField("title", data.title || "");
        setField("description", data.description || "");
        setField("time", fromApiTimeToLocal(data.time || ""));
        setField("location", data.location || "");
        setField("capacity", String(data.capacity ?? ""));
        setField("organizers", toCSV(data.organizers || []));
        setField("speakers", toCSV(data.speakers || []));
      } catch (e) {
        toast.error(`Failed to load event ${eventId}: ${e.message}`);
      }
    }
    load();
    return () => {
      ignore = true;
    };
  }, [mode, eventId, initial, setField, toast]);

  const onSubmit = async (e) => {
    e.preventDefault();
    // Validate
    if (!values.title.trim()) return toast.error("Title is required");
    if (!values.time || !isIsoLike(values.time)) return toast.error("Time must be set (YYYY-MM-DDTHH:MM)");
    const cap = parseCapacity(values.capacity);
    if (Number.isNaN(cap)) return toast.error("Capacity must be a non-negative integer");

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
        const res = await apiJson(`/api/events`, {
          method: "POST",
          body: JSON.stringify(payload),
        });
        toast.success(res?.message || "Event created successfully");
        onCreated?.(res);
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
          toast.info("No changes to save");
          return;
        }
        const res = await apiJson(`/api/events/${eventId}`, {
          method: "PATCH",
          body: JSON.stringify(patch),
        });
        toast.success(res?.message || "Event updated successfully");
        onUpdated?.(res);
      }
    } catch (e) {
      toast.error(e.message || "Request failed");
    }
  };

  return (
    <form onSubmit={onSubmit} className="grid gap-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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

      <div className="flex items-center gap-2">
        <Button type="submit" variant="primary">
          {mode === "create" ? "Create event" : "Save changes"}
        </Button>
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}

// ----------------------
// Delete Confirmation Modal (simple inline)
// ----------------------
function Confirm({ open, title, description, onConfirm, onCancel }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/30">
      <div className="w-[92vw] max-w-md rounded-2xl bg-white p-5 shadow-2xl">
        <h3 className="text-base font-semibold text-slate-900">{title}</h3>
        <p className="mt-1 text-sm text-slate-600">{description}</p>
        <div className="mt-4 flex justify-end gap-2">
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

  // UI state
  const [activeTab, setActiveTab] = useState("admin"); // "admin" | "user"
  const [mode, setMode] = useState("create"); // "create" | "edit"
  const [editId, setEditId] = useState("");
  const [showConfirm, setShowConfirm] = useState(false);

  const selected = useMemo(() => localEvents.find((e) => String(e.id) === String(editId)), [localEvents, editId]);

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
  };

  const handleUpdated = async (res) => {
    const id = res?.id ?? editId;
    // Re-fetch the canonical event for accuracy (uses GET /api/events/:id)
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
    } catch (e) {
      toast.error(e.message || "Delete failed");
    }
  };

  const loadForEdit = async () => {
    if (!editId) return toast.error("Enter an event ID to load");
    try {
      await apiJson(`/api/events/${editId}`, { method: "GET" });
      // Success only indicates it exists; form fetches actual fields itself.
      setMode("edit");
      toast.success(`Loaded event ${editId} for editing`);
    } catch (e) {
      toast.error(e.message || "Failed to load event");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top bar */}
      <div className="sticky top-0 z-30 border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-2xl bg-rose-700 text-white grid place-items-center font-bold">A</div>
            <div className="font-semibold">AUB Events – Admin</div>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Button variant={activeTab === "admin" ? "primary" : "secondary"} onClick={() => setActiveTab("admin")}>
              Admin Area
            </Button>
            <Button variant={activeTab === "user" ? "primary" : "secondary"} onClick={() => setActiveTab("user")}>
              Switch to User
            </Button>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-6xl px-4 py-6">
        {activeTab === "user" ? (
          <div className="rounded-2xl bg-white p-6 shadow-sm border border-slate-200">
            <h2 className="text-lg font-semibold">Welcome to user part</h2>
            <p className="mt-1 text-sm text-slate-600">
              This is a placeholder. In the next phase, admins will also browse events here as regular users.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left column: create/edit form */}
            <div className="lg:col-span-2 rounded-2xl bg-white p-6 shadow-sm border border-slate-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">
                  {mode === "create" ? "Create a new event" : `Edit event #${editId}`}
                </h2>
                {mode === "edit" && (
                  <div className="flex items-center gap-2">
                    <Button variant="secondary" onClick={() => { setMode("create"); setEditId(""); }}>
                      New
                    </Button>
                    <Button variant="danger" onClick={() => setShowConfirm(true)}>Delete</Button>
                  </div>
                )}
              </div>
              <div className="mt-4">
                <EventForm
                  mode={mode}
                  eventId={editId}
                  onCreated={handleCreated}
                  onUpdated={handleUpdated}
                  onCancel={() => { setMode("create"); setEditId(""); }}
                  toast={toast}
                />
              </div>
            </div>

            {/* Right column: quick tools and local cache */}
            <div className="rounded-2xl bg-white p-6 shadow-sm border border-slate-200">
              <h3 className="text-base font-semibold">Quick tools</h3>
              <div className="mt-3 grid gap-2">
                <div className="grid grid-cols-[1fr_auto] gap-2">
                  <TextInput
                    placeholder="Event ID"
                    value={editId}
                    onChange={(e) => setEditId(e.target.value)}
                  />
                  <Button variant="secondary" onClick={loadForEdit}>Load</Button>
                </div>
                <p className="text-xs text-slate-600">
                  Enter an event ID and click Load to edit it. The form will fetch current data using
                  <code className="ml-1 rounded bg-slate-100 px-1">GET /api/events/:id</code>.
                </p>
              </div>

              <div className="mt-6">
                <h4 className="text-sm font-semibold text-slate-700">Session events (local cache)</h4>
                <p className="text-xs text-slate-600">Recently created/edited events this session.</p>
                <div className="mt-3 grid gap-2">
                  {localEvents.length === 0 ? (
                    <div className="text-xs text-slate-500">No local events yet.</div>
                  ) : (
                    <ul className="divide-y divide-slate-200 border border-slate-200 rounded-xl overflow-hidden">
                      {localEvents.map((e) => (
                        <li key={e.id} className="p-3 hover:bg-slate-50 flex items-center justify-between">
                          <div>
                            <div className="text-sm font-semibold">#{String(e.id)} – {e.title || "Untitled"}</div>
                            <div className="text-xs text-slate-600">{e.location} • {fromApiTimeToLocal(e.time)}</div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Button variant="secondary" onClick={() => { setEditId(String(e.id)); setMode("edit"); }}>Edit</Button>
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
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
