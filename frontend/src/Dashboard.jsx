import { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { Calendar, MapPin, Users, Clock, Search, LogOut, CheckCircle, Plus, Filter } from 'lucide-react';
import { api } from './api';
import './Dashboard.css';

const CATEGORY_OPTIONS = ['Workshop', 'Concert', 'Lecture', 'Sports', 'Social', 'Career'];

function useToasts(timeout = 3600) {
  const [toasts, setToasts] = useState([]);
  const timers = useRef(new Map());

  useEffect(() => {
    return () => {
      timers.current.forEach(clearTimeout);
      timers.current.clear();
    };
  }, []);

  const dismiss = (id) => {
    setToasts((items) => items.filter((t) => t.id !== id));
    const timer = timers.current.get(id);
    if (timer) {
      clearTimeout(timer);
      timers.current.delete(id);
    }
  };

  const add = (variant, msg) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((items) => [...items, { id, variant, msg }]);
    const timer = setTimeout(() => dismiss(id), timeout);
    timers.current.set(id, timer);
  };

  return {
    toasts,
    success: (msg) => add('success', msg),
    error: (msg) => add('error', msg),
    info: (msg) => add('info', msg),
    dismiss,
  };
}

function Toasts({ items, dismiss }) {
  if (!items.length) return null;
  return (
    <div className="dash-toast-container">
      {items.map((t) => (
        <div key={t.id} className={`dash-toast dash-toast-${t.variant}`}>
          <span>{t.msg}</span>
          <button
            type="button"
            className="dash-toast-close"
            onClick={() => dismiss(t.id)}
            aria-label="Dismiss notification"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
}

function Dashboard() {
  const [user, setUser] = useState({ name: 'User', email: '', isAdmin: false });
  const [events, setEvents] = useState([]);
  const [allEvents, setAllEvents] = useState([]);
  const [registeredEvents, setRegisteredEvents] = useState([]);
  const [myEventIds, setMyEventIds] = useState(new Set());
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('all');
  const [showAllEvents, setShowAllEvents] = useState(false); // Show/hide all events
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [onlyAvailable, setOnlyAvailable] = useState(false);
  const [withinNextWeek, setWithinNextWeek] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const toast = useToasts();
  const lastFetchArgs = useRef({ path: '/api/events', auth: false, q: '' });
  const [detailOpen, setDetailOpen] = useState(false);
  const [detailEvent, setDetailEvent] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState('');

  const refreshAllEvents = useCallback(async () => {
    try {
      const res = await api('/api/events', { method: 'GET' });
      const fetched = res.events || [];
      setAllEvents(fetched);
      return fetched;
    } catch {
      return allEvents;
    }
  }, [allEvents]);

  const refreshRegisteredEvents = useCallback(async () => {
    try {
      const res = await api('/api/my/events', { method: 'GET', auth: true });
      const registered = res.events || [];
      setRegisteredEvents(registered);
      setMyEventIds(new Set(registered.map((e) => e.id)));
      return registered;
    } catch {
      return registeredEvents;
    }
  }, [registeredEvents]);

  // Detect mobile screen size
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    setShowAllEvents(false);
  }, [categoryFilter, onlyAvailable, withinNextWeek]);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoading(true);
        // Load user profile
        try {
          const me = await api('/auth/me/', { auth: true });
          if (!cancelled) setUser({
            name: me.name || me.email.split('@')[0],
            email: me.email,
            isAdmin: me.is_admin || me.isAdmin || false
          });
        } catch {
          const cached = localStorage.getItem('user');
          if (cached && !cancelled) {
            const u = JSON.parse(cached);
            const display = u.name || (u.email ? u.email.split('@')[0] : 'User');
            setUser({
              name: display,
              email: u.email || '',
              isAdmin: u.is_admin || u.isAdmin || false
            });
          }
        }

        // Load all events (public) - initial load; search effect will also refetch when query/activeTab changes
        lastFetchArgs.current = { path: '/api/events', auth: false, q: '' };
        const list = await api('/api/events', { method: 'GET' });
        if (!cancelled) {
          const fetched = list.events || [];
          setEvents(fetched);
          setAllEvents(fetched);
        }

        // Load my registrations
        try {
          lastFetchArgs.current = { path: '/api/my/events', auth: true, q: '' };
          const mine = await api('/api/my/events', { method: 'GET', auth: true });
          const registered = mine.events || [];
          const ids = new Set(registered.map(e => e.id));
          if (!cancelled) {
            setRegisteredEvents(registered);
            setMyEventIds(ids);
          }
        } catch {
          // not logged or endpoint unavailable
        }
      } catch (e) {
        if (!cancelled) setError(e.message || 'Failed to load dashboard');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  // Fetch events from backend when the search query or active tab changes.
  useEffect(() => {
    let cancelled = false;
    const timer = setTimeout(async () => {
      try {
        setLoading(true);
        // Reset show more state when search/tab changes
        setShowAllEvents(false);
        const q = (query || '').trim();
        let path = activeTab === 'all' ? '/api/events' : '/api/my/events';
        if (q) path += `?q=${encodeURIComponent(q)}`;
        lastFetchArgs.current = { path, auth: activeTab !== 'all', q };
        const res = await api(path, { method: 'GET', auth: activeTab !== 'all' });
        if (cancelled) return;
        const fetched = res.events || [];
        setEvents(fetched);
        if (activeTab === 'all' && !q) {
          setAllEvents(fetched);
        }
        if (activeTab === 'registered' && !q) {
          setRegisteredEvents(fetched);
          setMyEventIds(new Set(fetched.map((e) => e.id)));
        }
        setError('');
      } catch (e) {
        if (!cancelled) {
          setError(e.message || 'Search failed');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 300); // debounce

    return () => { cancelled = true; clearTimeout(timer); };
  }, [query, activeTab]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    let result = events;
    const now = new Date();
    const weekCutoff = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);

    result = result.filter(e => {
      if (!e.time) {
        if (withinNextWeek) return false;
        return true;
      }
      const eventDate = new Date(e.time);
      if (Number.isNaN(eventDate.getTime())) return false;
      if (eventDate < now) return false;
      if (withinNextWeek && eventDate > weekCutoff) return false;
      return true;
    });

    if (categoryFilter !== 'all') {
      result = result.filter(e => (e.category || '').toLowerCase() === categoryFilter);
    }

    if (onlyAvailable) {
      result = result.filter(e => {
        if (typeof e.available_seats !== 'number') return true;
        return e.available_seats > 0;
      });
    }

    if (q) {
      result = result.filter(e =>
        String(e.title || '').toLowerCase().includes(q) ||
        String(e.location || '').toLowerCase().includes(q) ||
        String(e.description || '').toLowerCase().includes(q)
      );
    }

    if (activeTab === 'registered') {
      result = result.filter(e => myEventIds.has(e.id));
    }

    return [...result].sort((a, b) => {
      if (!a.time) return 1;
      if (!b.time) return -1;
      return new Date(a.time) - new Date(b.time);
    });
  }, [events, query, activeTab, myEventIds, categoryFilter, onlyAvailable, withinNextWeek]);

  const totalUpcomingCount = useMemo(() => {
    const now = Date.now();
    return allEvents.filter(evt => {
      if (!evt?.time) return false;
      const ts = new Date(evt.time).getTime();
      if (Number.isNaN(ts)) return false;
      return ts >= now;
    }).length;
  }, [allEvents]);

  const registeredUpcomingCount = useMemo(() => {
    const now = Date.now();
    return registeredEvents.filter(evt => {
      if (!evt?.time) return false;
      const ts = new Date(evt.time).getTime();
      if (Number.isNaN(ts)) return false;
      return ts >= now;
    }).length;
  }, [registeredEvents]);

  const normalizeList = (value) => {
    if (!value) return [];
    if (Array.isArray(value)) {
      return value.filter(Boolean);
    }
    if (typeof value === 'string') {
      return value.split(',').map((item) => item.trim()).filter(Boolean);
    }
    return [];
  };

  const onLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  };

  const register = async (event) => {
    const id = event.id;
    try {
      const res = await api('/api/events/register', { method: 'POST', body: { event_id: id }, auth: true });
      setMyEventIds((prev) => {
        const next = new Set(prev);
        next.add(id);
        return next;
      });
      setEvents(prev => prev.map(e => {
        if (e.id !== id) return e;
        const cur = typeof e.available_seats === 'number' ? e.available_seats : null;
        if (cur === null) return e;
        return { ...e, available_seats: Math.max(0, cur - 1) };
      }));
      setAllEvents(prev => prev.map(e => {
        if (e.id !== id) return e;
        const cur = typeof e.available_seats === 'number' ? e.available_seats : null;
        if (cur === null) return e;
        return { ...e, available_seats: Math.max(0, cur - 1) };
      }));
      setRegisteredEvents(prev => {
        const exists = prev.some(e => e.id === id);
        if (exists) {
          return prev.map(e => {
            if (e.id !== id) return e;
            const cur = typeof e.available_seats === 'number' ? e.available_seats : null;
            if (cur === null) return e;
            return { ...e, available_seats: Math.max(0, cur - 1) };
          });
        }
        const initialSeats = typeof event.available_seats === 'number'
          ? Math.max(0, event.available_seats - 1)
          : event.available_seats;
        return [...prev, { ...event, available_seats: initialSeats }];
      });
      const trimmedQuery = (query || '').trim();
      const [latestRegistered, latestAll] = await Promise.all([
        refreshRegisteredEvents(),
        refreshAllEvents(),
      ]);
      if (activeTab === 'registered' && !trimmedQuery) {
        setEvents(latestRegistered);
      }
      if (activeTab === 'all' && !trimmedQuery) {
        setEvents(latestAll);
      }
      toast.success(res?.message || `You registered for ${event.title || 'the event'}.`);
      if (typeof window !== 'undefined' && window.confirm('Add this event to Google Calendar?')) {
        startCalendarFlow(event);
      }
    } catch (e) {
      toast.error(e.message || 'Registration failed');
    }
  };

  const unregister = async (event) => {
    const id = event.id;
    const confirmed = window.confirm(`Unregister from "${event.title || 'this event'}"?`);
    if (!confirmed) return;
    try {
      const res = await api('/api/events/unregister', { method: 'POST', body: { event_id: id }, auth: true });
      setMyEventIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
      setEvents(prev => prev.map(e => {
        if (e.id !== id) return e;
        const cur = typeof e.available_seats === 'number' ? e.available_seats : null;
        const cap = typeof e.capacity === 'number' ? e.capacity : null;
        if (cur === null) return e;
        const next = Math.min(cap ?? cur + 1, cur + 1);
        return { ...e, available_seats: next };
      }));
      setAllEvents(prev => prev.map(e => {
        if (e.id !== id) return e;
        const cur = typeof e.available_seats === 'number' ? e.available_seats : null;
        const cap = typeof e.capacity === 'number' ? e.capacity : null;
        if (cur === null) return e;
        const next = Math.min(cap ?? cur + 1, cur + 1);
        return { ...e, available_seats: next };
      }));
      setRegisteredEvents(prev => prev.filter(e => e.id !== id));
      if (activeTab === 'registered') {
        setEvents(prev => prev.filter(e => e.id !== id));
      }
      const trimmedQuery = (query || '').trim();
      const [latestRegistered, latestAll] = await Promise.all([
        refreshRegisteredEvents(),
        refreshAllEvents(),
      ]);
      if (activeTab === 'registered' && !trimmedQuery) {
        setEvents(latestRegistered);
      }
      if (activeTab === 'all' && !trimmedQuery) {
        setEvents(latestAll);
      }
      toast.success(res?.message || `You unregistered from ${event.title || 'the event'}.`);
    } catch (e) {
      toast.error(e.message || 'Unregistration failed');
    }
  };

  const retryLastFetch = async () => {
    const { path, auth, q } = lastFetchArgs.current;
    if (!path) return;
    try {
      setLoading(true);
      setError('');
      const res = await api(path, { method: 'GET', auth });
      const fetched = res.events || [];
      setEvents(fetched);
      if (auth) {
        if (!q) {
          setRegisteredEvents(fetched);
          setMyEventIds(new Set(fetched.map((e) => e.id)));
        }
      } else if (!q) {
        setAllEvents(fetched);
      }
    } catch (e) {
      setError(e.message || 'Request failed');
    } finally {
      setLoading(false);
    }
  };

  const openDetails = async (event) => {
    setDetailOpen(true);
    setDetailError('');
    setDetailEvent(event);
    setDetailLoading(true);
    try {
      const res = await api(`/api/events/${event.id}`, { method: 'GET', auth: true });
      if (res) {
        setDetailEvent((prev) => ({ ...(prev || {}), ...res }));
      }
    } catch (err) {
      setDetailError(err.message || 'Failed to load event details');
    } finally {
      setDetailLoading(false);
    }
  };

  const closeDetails = () => {
    setDetailOpen(false);
    setDetailEvent(null);
    setDetailError('');
    setDetailLoading(false);
  };

  const FALLBACK_EVENT = {
    title: 'Sample Event Title',
    description: 'Here is a short description of the event for attendees.',
    location: '123 Event Street, Cityville'
  };
  const FALLBACK_START_ISO = '2025-12-12T15:00:00Z';
  const DEFAULT_DURATION_MINUTES = 60;

  const toIcsDate = (date) => {
    return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
  };

  const computeEventTimes = (event) => {
    let startDate = event?.time ? new Date(event.time) : null;
    if (!startDate || Number.isNaN(startDate.getTime())) {
      startDate = new Date(FALLBACK_START_ISO);
    }

    let endDate;
    const rawEnd = event?.end_time || event?.endTime;
    if (rawEnd) {
      const parsedEnd = new Date(rawEnd);
      if (!Number.isNaN(parsedEnd.getTime())) {
        endDate = parsedEnd;
      }
    }

    if (!endDate) {
      endDate = new Date(startDate.getTime() + DEFAULT_DURATION_MINUTES * 60 * 1000);
    }

    if (Number.isNaN(endDate.getTime())) {
      endDate = new Date(startDate.getTime() + DEFAULT_DURATION_MINUTES * 60 * 1000);
    }

    return { startDate, endDate };
  };

  const openGoogleCalendar = (event, { startDate, endDate }) => {
    const format = (date) => toIcsDate(date);
    const params = new URLSearchParams({
      action: 'TEMPLATE',
      text: event?.title || FALLBACK_EVENT.title,
      details: event?.description || FALLBACK_EVENT.description,
      location: event?.location || FALLBACK_EVENT.location,
      dates: `${format(startDate)}/${format(endDate)}`
    });
    window.open(`https://calendar.google.com/calendar/render?${params.toString()}`, '_blank', 'noopener,noreferrer');
  };

  const startCalendarFlow = (event) => {
    const times = computeEventTimes(event);
    if (typeof window === 'undefined') return;
    openGoogleCalendar(event, times);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <div className="user-info">
            <div className="avatar">{user.name.charAt(0).toUpperCase()}</div>
            <div>
              <h1>Welcome back, {user.name}!</h1>
              <p className="user-email">{user.email}</p>
            </div>
          </div>
          <div className="header-actions">
            {user.isAdmin && (
              <button className="btn btn-secondary" onClick={() => window.location.href = '/admin'}>
                📋 Admin Area
              </button>
            )}
            <button className="logout-btn" onClick={onLogout}>
              <LogOut size={18} />
              Log out
            </button>
          </div>
        </div>
      </div>

      <div className="dashboard-main">
        <div className="stats-grid">
          <div className="stat-card">
            <Calendar className="stat-icon" />
            <div>
              <h3>{totalUpcomingCount}</h3>
              <p>Total Events</p>
            </div>
          </div>
          <div className="stat-card">
            <CheckCircle className="stat-icon registered" />
            <div>
              <h3>{registeredUpcomingCount}</h3>
              <p>Registered Events</p>
            </div>
          </div>
        </div>

        <div className="events-section">
          <div className="section-header">
            <h2>Events</h2>
            <div className="tabs">
              <button
                className={`tab ${activeTab === 'all' ? 'active' : ''}`}
                onClick={() => setActiveTab('all')}
              >
                All Events
              </button>
              <button
                className={`tab ${activeTab === 'registered' ? 'active' : ''}`}
                onClick={() => setActiveTab('registered')}
              >
                My Events
              </button>
            </div>
          </div>

          <div className="search-row">
            <div className="search-bar">
              <Search className="search-icon" size={20} />
              <input
                type="text"
                placeholder="Search events by title, location, or description..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>
            <button
              type="button"
              className="filter-button"
              onClick={() => setShowFilters((prev) => !prev)}
              aria-expanded={showFilters}
            >
              <Filter size={18} />
              Filters
              {(categoryFilter !== 'all' || onlyAvailable || withinNextWeek) && !showFilters && (
                <span className="filter-indicator" aria-hidden="true">• Active</span>
              )}
              <span className="filter-caret">{showFilters ? '▲' : '▼'}</span>
            </button>
          </div>

          {showFilters && (
            <div className="filter-panel">
              <div className="filter-group">
                <label className="filter-label" htmlFor="category-filter">Category</label>
                <select
                  id="category-filter"
                  className="filter-select"
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                >
                  <option value="all">All categories</option>
                  {CATEGORY_OPTIONS.map((option) => (
                    <option key={option} value={option.toLowerCase()}>{option}</option>
                  ))}
                </select>
              </div>
              <label className="filter-toggle">
                <input
                  type="checkbox"
                  checked={onlyAvailable}
                  onChange={(e) => setOnlyAvailable(e.target.checked)}
                />
                <span>Only events with seats</span>
              </label>
              <label className="filter-toggle">
                <input
                  type="checkbox"
                  checked={withinNextWeek}
                  onChange={(e) => setWithinNextWeek(e.target.checked)}
                />
                <span>Next 7 days</span>
              </label>
            </div>
          )}

          {loading ? (
            <div className="loading">Loading events...</div>
          ) : error ? (
            <div className="error">
              <div>{error}</div>
              <button type="button" className="error-retry-button" onClick={retryLastFetch}>
                Try Again
              </button>
            </div>
          ) : (
            <>
              {(query.trim() || categoryFilter !== 'all' || onlyAvailable || withinNextWeek || activeTab === 'registered') && (
                <div className="results-summary">
                  {filtered.length} {filtered.length === 1 ? 'event' : 'events'} found
                </div>
              )}
              <div className="events-grid">
                {filtered.length === 0 ? (
                  <div className="no-events">
                    {activeTab === 'registered' ?
                      "You haven't registered for any events yet." :
                      "No events match your search."
                    }
                  </div>
                ) : (
                  <>
                    {(showAllEvents ? filtered : filtered.slice(0, isMobile ? 4 : 6)).map(evt => (
                      <div key={evt.id} className={`event-card ${myEventIds.has(evt.id) ? 'registered' : ''}`}>
                        {evt.image_url && (
                          <div className="event-card-image">
                            <img src={evt.image_url} alt={`${evt.title || 'Event'} poster`} onError={(e) => { e.currentTarget.style.display = 'none'; }} />
                          </div>
                        )}
                        <div className="event-header">
                          <h3>{evt.title}</h3>
                          {myEventIds.has(evt.id) && <CheckCircle className="registered-badge" size={20} />}
                        </div>

                        {evt.category && (
                          <span className={`category-badge category-${evt.category.toLowerCase()}`}>
                            {evt.category}
                          </span>
                        )}

                        {evt.description && (
                          <p className="event-description">{evt.description}</p>
                        )}

                        <div className="event-details">
                          {evt.time && (
                            <div className="detail">
                              <Clock size={16} />
                              <span>{formatDate(evt.time)}</span>
                            </div>
                          )}
                          {evt.location && (
                            <div className="detail">
                              <MapPin size={16} />
                              <span>{evt.location}</span>
                            </div>
                          )}
                          {typeof evt.capacity === 'number' && (
                            <div className="detail">
                              <Users size={16} />
                              <span>
                                Capacity: {evt.capacity}
                                {typeof evt.available_seats === 'number' && (
                                  <>
                                    <span> · </span>
                                    {evt.available_seats <= 0 ? (
                                      <strong>Full</strong>
                                    ) : (
                                      <strong>Available: {evt.available_seats}</strong>
                                    )}
                                  </>
                                )}
                              </span>
                            </div>
                          )}
                        </div>

                        <div className="event-actions">
                          <button
                            type="button"
                            className="btn btn-outline event-details-btn"
                            onClick={() => openDetails(evt)}
                          >
                            View Details
                          </button>
                          {myEventIds.has(evt.id) ? (
                            <button
                              onClick={() => unregister(evt)}
                              className="btn btn-secondary"
                            >
                              Unregister
                            </button>
                          ) : (
                            (() => {
                              const isFull = typeof evt.available_seats === 'number' && evt.available_seats <= 0;
                              return (
                                <button
                                  onClick={() => register(evt)}
                                  className={`btn ${isFull ? 'btn-disabled' : 'btn-primary'}`}
                                  disabled={isFull}
                                  title={isFull ? 'Event is full' : 'Register'}
                                >
                                  {isFull ? 'Full' : (<><Plus size={16} /> Register</>)}
                                </button>
                              );
                            })()
                          )}
                        </div>
                      </div>
                    ))}

                    {filtered.length > (isMobile ? 4 : 6) && (
                      <div className="show-more-section">
                        <button
                          className="btn btn-secondary show-more-btn"
                          onClick={() => setShowAllEvents(!showAllEvents)}
                        >
                          {showAllEvents ? '📈 Show Less' : `📋 Show More (${filtered.length - (isMobile ? 4 : 6)} more)`}
                        </button>
                      </div>
                    )}
                  </>
                )}
              </div>
            </>
          )}
        </div>
      </div>
      <Toasts items={toast.toasts} dismiss={toast.dismiss} />
      {detailOpen && (
        <div className="dashboard-modal-overlay" role="dialog" aria-modal="true" onClick={closeDetails}>
          <div className="dashboard-modal" onClick={(e) => e.stopPropagation()}>
            <button type="button" className="dashboard-modal-close" onClick={closeDetails} aria-label="Close details">
              ×
            </button>
            {detailLoading ? (
              <div className="dashboard-modal-loading">Loading event details...</div>
            ) : detailError ? (
              <div className="dashboard-modal-error">{detailError}</div>
            ) : detailEvent ? (
              <div className="dashboard-modal-content">
                <h3 className="dashboard-modal-title">{detailEvent.title}</h3>
                {detailEvent.time && (
                  <div className="dashboard-modal-meta">
                    <Clock size={16} />
                    <span>{formatDate(detailEvent.time)}</span>
                  </div>
                )}
                {detailEvent.location && (
                  <div className="dashboard-modal-meta">
                    <MapPin size={16} />
                    <span>{detailEvent.location}</span>
                  </div>
                )}
                <div className="dashboard-modal-meta">
                  <Users size={16} />
                  <span>
                    Capacity: {detailEvent.capacity}
                    {typeof detailEvent.available_seats === 'number' && (
                      <>
                        <span> · </span>
                        {detailEvent.available_seats <= 0 ? 'Full' : `Available: ${detailEvent.available_seats}`}
                      </>
                    )}
                  </span>
                </div>
                {detailEvent.category && (
                  <div className="dashboard-modal-category">
                    <span className={`category-badge category-${detailEvent.category.toLowerCase()}`}>
                      {detailEvent.category}
                    </span>
                  </div>
                )}
                {detailEvent.image_url && (
                  <div className="dashboard-modal-image">
                    <img src={detailEvent.image_url} alt={`${detailEvent.title || 'Event'} poster`} />
                  </div>
                )}
                {detailEvent.description && (
                  <p className="dashboard-modal-description">{detailEvent.description}</p>
                )}
                {normalizeList(detailEvent.organizers).length > 0 && (
                  <div className="dashboard-modal-section">
                    <h4>Organizers</h4>
                    <ul>
                      {normalizeList(detailEvent.organizers).map((org) => (
                        <li key={`org-${org}`}>{org}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {normalizeList(detailEvent.speakers).length > 0 && (
                  <div className="dashboard-modal-section">
                    <h4>Speakers</h4>
                    <ul>
                      {normalizeList(detailEvent.speakers).map((speaker) => (
                        <li key={`speaker-${speaker}`}>{speaker}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="dashboard-modal-error">Event details unavailable.</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;