
import React, { useState } from "react";
import "./Auth.css";
import { api } from './api';

export default function Signup({ onSwitch }) {
  // Prefill demo values but allow editing
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [step, setStep] = useState(1); // 1=signup form, 2=verify form
  const [loading, setLoading] = useState(false);
  const [verificationCode, setVerificationCode] = useState("");
  const [serverTokenHint, setServerTokenHint] = useState(null); // dev helper
  const [error, setError] = useState("");

  const handleSignup = async (e) => {
    e.preventDefault();
    setError("");
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    try {
      setLoading(true);
      const res = await api('/auth/signup/', { method: 'POST', body: { email, password } });
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
      window.location.href = '/login';
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
            <p style={{fontSize:'0.8rem', opacity:0.7}}>Dev hint code: {serverTokenHint}</p>
          )}
          <input type="text" value={verificationCode} onChange={e => setVerificationCode(e.target.value)} placeholder="Verification Code" required />
          <button type="submit" disabled={loading}>{loading ? 'Verifying...' : 'Verify'}</button>
          {error && <div className="flash err">{error}</div>}
        </form>
      )}
      <p>
        Already have an account? <button className="link" onClick={onSwitch}>Login</button>
      </p>
    </div>
  );
}
