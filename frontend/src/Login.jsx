
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from './api';

export default function Login({ onSwitch, onForgot }) {
  // Use the signup email/password if available, else blank
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");

  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      setLoading(true);
      const data = await api('/auth/login/', { method: 'POST', body: { email, password } });
      if (data.token) localStorage.setItem('token', data.token);
      // Tentatively store user with derived name; will refine after /auth/me
      localStorage.setItem('user', JSON.stringify({ email, name: email.split('@')[0] }));
      // After login, check if user is admin and route accordingly
      try {
        const me = await api('/auth/me/', { auth: true });
        if (me?.name) {
          localStorage.setItem('user', JSON.stringify({ email: me.email, name: me.name }));
        }
        if (me?.is_admin) {
          navigate('/admin', { replace: true });
          return;
        }
      } catch (_) {
        // ignore and fall back to dashboard
      }
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container login-bg">
      <h2 className="login-title">Login</h2>
      <form onSubmit={handleSubmit}>
        <input type="email" name="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" required style={{ fontSize: '1.2rem' }} />
        <input type="password" name="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" required style={{ fontSize: '1.2rem' }} />
        <button type="submit" style={{ fontSize: '1.2rem', padding: '1rem' }} disabled={loading}>{loading ? 'Logging in...' : 'Log In'}</button>
        {error && <div className="flash err" style={{ marginTop: '0.5rem' }}>{error}</div>}
      </form>
      <div className="login-links">
        <button className="link" onClick={() => onForgot ? onForgot() : navigate('/forgot')}>Forgot Password?</button>
        <span> | </span>
        <button className="link" onClick={() => onSwitch ? onSwitch() : navigate('/signup')}>Sign Up</button>
      </div>
    </div>
  );
}
