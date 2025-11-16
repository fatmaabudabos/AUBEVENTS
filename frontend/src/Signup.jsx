
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Auth.css";
import { api } from './api';

export default function Signup({ onSwitch }) {
  // Prefill demo values but allow editing
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [step, setStep] = useState(1); // 1=signup form, 2=verify form
  const [loading, setLoading] = useState(false);
  const [verificationCode, setVerificationCode] = useState("");
  const [serverTokenHint, setServerTokenHint] = useState(null); // dev helper
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    setError("");
    const trimmedFirst = firstName.trim();
    const trimmedLast = lastName.trim();
    if (!trimmedFirst || !trimmedLast) {
      setError('First and last name are required');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    try {
      setLoading(true);
      const res = await api('/auth/signup/', {
        method: 'POST',
        body: { first_name: trimmedFirst, last_name: trimmedLast, email, password },
      });
      // In development the backend returns verification_token for convenience
      if (res.verification_token) setServerTokenHint(res.verification_token);
      setStep(2);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setError("");
    try {
      setLoading(true);
      await api('/auth/verify/', { method: 'POST', body: { email, token: verificationCode } });
      // Auto-login after successful verification, then redirect by role
      try {
        const loginRes = await api('/auth/login/', { method: 'POST', body: { email, password } });
        if (loginRes?.token) localStorage.setItem('token', loginRes.token);
        // Store display name for dashboard welcome
        const displayFirst = firstName.trim();
        const displayLast = lastName.trim();
        localStorage.setItem('user', JSON.stringify({
          email,
          name: displayFirst || email.split('@')[0],
          firstName: displayFirst,
          lastName: displayLast,
        }));
        try {
          const me = await api('/auth/me/', { auth: true });
          if (me?.name) {
            localStorage.setItem('user', JSON.stringify({
              email: me.email,
              name: me.name,
              firstName: me.first_name,
              lastName: me.last_name,
            }));
          }
          if (me?.is_admin) {
            navigate('/admin', { replace: true });
            return;
          }
        } catch (_) { /* fallthrough to dashboard */ }
        navigate('/dashboard', { replace: true });
      } catch (_) {
        // Fallback to login screen if auto-login fails
        navigate('/login', { replace: true });
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h2>Sign Up</h2>
      {step === 1 ? (
        <form onSubmit={handleSignup}>
          <div className="auth-row">
            <input
              type="text"
              name="first_name"
              value={firstName}
              onChange={e => setFirstName(e.target.value)}
              placeholder="First name"
              required
            />
            <input
              type="text"
              name="last_name"
              value={lastName}
              onChange={e => setLastName(e.target.value)}
              placeholder="Last name"
              required
            />
          </div>
          <input type="email" name="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" required />
          <input type="password" name="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password (min 8 chars)" minLength={8} required />
          <input type="password" name="confirmPassword" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} placeholder="Confirm Password" minLength={8} required />
          <button type="submit" disabled={loading}>{loading ? 'Signing Up...' : 'Sign Up'}</button>
          {error && <div className="flash err">{error}</div>}
        </form>
      ) : (
        <form onSubmit={handleVerify}>
          <p>Enter the verification code sent to <b>{email}</b>.</p>
          {serverTokenHint && (
            <p style={{ fontSize: '0.8rem', opacity: 0.7 }}>Dev hint code: {serverTokenHint}</p>
          )}
          <input type="text" value={verificationCode} onChange={e => setVerificationCode(e.target.value)} placeholder="Verification Code" required />
          <button type="submit" disabled={loading}>{loading ? 'Verifying...' : 'Verify'}</button>
          {error && <div className="flash err">{error}</div>}
        </form>
      )}
      <p>
        Already have an account? <button className="link" onClick={() => onSwitch ? onSwitch() : navigate('/login')}>Login</button>
      </p>
    </div>
  );
}
