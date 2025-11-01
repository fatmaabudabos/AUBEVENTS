
import React, { useState } from "react";
import { useNavigate } from 'react-router-dom';
import "./Auth.css";
import { api } from './api';

export default function ForgotPassword({ onSwitchLogin }) {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleRequest = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api('/auth/password-reset-request/', {
        method: 'POST',
        body: { email },
      });
      setStep(2);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="auth-container">
      <h2>Forgot Password</h2>
      {step === 1 ? (
        <form onSubmit={handleRequest}>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Enter your email" required />
          <button type="submit">Send Reset Link</button>
          {error && <div className="flash err">{error}</div>}
        </form>
      ) : (
        <div>
          <p>We have sent a password reset link to your email. Please check your inbox and follow the link to reset your password.</p>
          <a href="#" onClick={(e) => { e.preventDefault(); onSwitchLogin ? onSwitchLogin() : navigate('/login'); }}>Back to Login</a>
        </div>
      )}
      <p>
        Remembered? <button className="link" onClick={() => onSwitchLogin ? onSwitchLogin() : navigate('/login')}>Back to Login</button>
      </p>
    </div>
  );
}
