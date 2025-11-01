import { useState, useEffect, useMemo } from 'react';
import { Calendar, MapPin, Users, Clock, Search, LogOut, CheckCircle, Plus } from 'lucide-react';
import { api } from './api';
import './Dashboard.css';

function Dashboard() {
  const [user, setUser] = useState({ name: 'User', email: '' });
  const [events, setEvents] = useState([]);
  const [myEventIds, setMyEventIds] = useState(new Set());
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoading(true);
        // Load user profile
        try {
          const me = await api('/auth/me/', { auth: true });
          if (!cancelled) setUser({ name: me.name || me.email.split('@')[0], email: me.email });
        } catch {
          const cached = localStorage.getItem('user');
          if (cached && !cancelled) {
            const u = JSON.parse(cached);
            const display = u.name || (u.email ? u.email.split('@')[0] : 'User');
            setUser({ name: display, email: u.email || '' });
          }
        }

        // Load all events (public) - initial load; search effect will also refetch when query/activeTab changes
        const list = await api('/api/events', { method: 'GET' });
        if (!cancelled) setEvents(list.events || []);

        // Load my registrations
        try {
          const mine = await api('/api/my/events', { method: 'GET', auth: true });
          const ids = new Set((mine.events || []).map(e => e.id));
          if (!cancelled) setMyEventIds(ids);
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
        const q = (query || '').trim();
        let path = activeTab === 'all' ? '/api/events' : '/api/my/events';
        if (q) path += `?q=${encodeURIComponent(q)}`;
        const res = await api(path, { method: 'GET', auth: activeTab !== 'all' });
        if (cancelled) return;
        setEvents(res.events || []);
        // Keep myEventIds in sync when viewing registered events
        if (activeTab === 'registered') {
          const ids = new Set((res.events || []).map(e => e.id));
          setMyEventIds(ids);
        }
        setError('');
      } catch (e) {
        if (!cancelled) setError(e.message || 'Search failed');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 300); // debounce

    return () => { cancelled = true; clearTimeout(timer); };
  }, [query, activeTab]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    let result = events;

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

    return result;
  }, [events, query, activeTab, myEventIds]);

  const onLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  };

  const register = async (id) => {
    try {
      const res = await api('/api/events/register', { method: 'POST', body: { event_id: id }, auth: true });
      // Mark as registered
      setMyEventIds(prev => new Set([...Array.from(prev), id]));
      // Optimistically decrement available seats in local state
      setEvents(prev => prev.map(e => {
        if (e.id !== id) return e;
        const cur = typeof e.available_seats === 'number' ? e.available_seats : null;
        if (cur === null) return e;
        const next = Math.max(0, cur - 1);
        return { ...e, available_seats: next };
      }));
      if (res && res.message) {
        // Optional: lightweight feedback
        // console.log(res.message);
      }
    } catch (e) {
      alert(e.message || 'Registration failed');
    }
  };

  const unregister = async (id) => {
    try {
      const res = await api('/api/events/unregister', { method: 'POST', body: { event_id: id }, auth: true });
      // Remove from my registrations
      setMyEventIds(prev => { const copy = new Set(prev); copy.delete(id); return copy; });
      // Optimistically increment available seats (bounded by capacity)
      setEvents(prev => prev.map(e => {
        if (e.id !== id) return e;
        const cur = typeof e.available_seats === 'number' ? e.available_seats : null;
        const cap = typeof e.capacity === 'number' ? e.capacity : null;
        if (cur === null) return e;
        const next = Math.min(cap ?? cur + 1, cur + 1);
        return { ...e, available_seats: next };
      }));
      if (res && res.message) {
        // Optional: lightweight feedback
        // console.log(res.message);
      }
    } catch (e) {
      alert(e.message || 'Unregistration failed');
    }
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
          <button className="logout-btn" onClick={onLogout}>
            <LogOut size={18} />
            Log out
          </button>
        </div>
      </div>

      <div className="dashboard-main">
        <div className="stats-grid">
          <div className="stat-card">
            <Calendar className="stat-icon" />
            <div>
              <h3>{events.length}</h3>
              <p>Total Events</p>
            </div>
          </div>
          <div className="stat-card">
            <CheckCircle className="stat-icon registered" />
            <div>
              <h3>{myEventIds.size}</h3>
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

          <div className="search-bar">
            <Search className="search-icon" size={20} />
            <input
              type="text"
              placeholder="Search events by title, location, or description..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>

          {loading ? (
            <div className="loading">Loading events...</div>
          ) : error ? (
            <div className="error">{error}</div>
          ) : (
            <div className="events-grid">
              {filtered.length === 0 ? (
                <div className="no-events">
                  {activeTab === 'registered' ?
                    "You haven't registered for any events yet." :
                    "No events match your search."
                  }
                </div>
              ) : (
                filtered.map(evt => (
                  <div key={evt.id} className={`event-card ${myEventIds.has(evt.id) ? 'registered' : ''}`}>
                    <div className="event-header">
                      <h3>{evt.title}</h3>
                      {myEventIds.has(evt.id) && <CheckCircle className="registered-badge" size={20} />}
                    </div>

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
                      {myEventIds.has(evt.id) ? (
                        <button
                          onClick={() => unregister(evt.id)}
                          className="btn btn-secondary"
                        >
                          Unregister
                        </button>
                      ) : (
                        (() => {
                          const isFull = typeof evt.available_seats === 'number' && evt.available_seats <= 0;
                          return (
                            <button
                              onClick={() => register(evt.id)}
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
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;