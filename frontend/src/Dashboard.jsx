import { useState, useEffect, useMemo } from 'react';
import { api } from './api';
import './Dashboard.css';

function Dashboard() {
  const [user, setUser] = useState({ name: 'User', email: '' });
  const [events, setEvents] = useState([]);
  const [myEventIds, setMyEventIds] = useState(new Set());
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoading(true);
        // Load user profile
        try {
          const me = await api('/auth/me/', { auth: true });
          if (!cancelled) setUser({ name: me.email.split('@')[0], email: me.email });
        } catch {
          const cached = localStorage.getItem('user');
          if (cached && !cancelled) {
            const u = JSON.parse(cached);
            setUser({ name: (u.email || u.name || 'User').split?.('@')[0] || 'User', email: u.email || '' });
          }
        }

        // Load all events (public)
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

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return events;
    return events.filter(e =>
      String(e.title || '').toLowerCase().includes(q) ||
      String(e.location || '').toLowerCase().includes(q) ||
      String(e.description || '').toLowerCase().includes(q)
    );
  }, [events, query]);

  const onLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  };

  const register = async (id) => {
    try {
      await api('/api/events/register', { method: 'POST', body: { event_id: id }, auth: true });
      setMyEventIds(prev => new Set([...Array.from(prev), id]));
    } catch (e) {
      alert(e.message || 'Registration failed');
    }
  };

  const unregister = async (id) => {
    try {
      await api('/api/events/unregister', { method: 'POST', body: { event_id: id }, auth: true });
      setMyEventIds(prev => { const copy = new Set(prev); copy.delete(id); return copy; });
    } catch (e) {
      alert(e.message || 'Unregistration failed');
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Welcome, {user.name}!</h1>
        <button className="logout-btn" onClick={onLogout}>Log out</button>
      </div>

      <div className="dashboard-main">
        <div className="events-section">
          <h2>Upcoming Events</h2>
          <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
            <input
              type="text"
              placeholder="Search by title, location, or description..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{ flex: 1, padding: '10px 12px', borderRadius: 6, border: '1px solid #ddd' }}
            />
          </div>

          {loading ? (
            <div>Loading…</div>
          ) : error ? (
            <div className="flash err">{error}</div>
          ) : (
            <div className="events-list">
              {filtered.length === 0 ? (
                <div>No events match your search.</div>
              ) : (
                filtered.map(evt => (
                  <div key={evt.id} className="event-card">
                    <h3>{evt.title}</h3>
                    {evt.time && (
                      <p style={{ margin: '6px 0' }}>🕒 {evt.time.replace('T', ' ')}</p>
                    )}
                    {evt.location && (
                      <p style={{ margin: '6px 0' }}>📍 {evt.location}</p>
                    )}
                    {typeof evt.capacity === 'number' && (
                      <p style={{ margin: '6px 0' }}>Capacity: {evt.capacity}</p>
                    )}
                    <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
                      {myEventIds.has(evt.id) ? (
                        <button onClick={() => unregister(evt.id)} className="logout-btn" style={{ background: '#6c757d' }}>Unregister</button>
                      ) : (
                        <button onClick={() => register(evt.id)} className="logout-btn" style={{ background: '#28a745' }}>Register</button>
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