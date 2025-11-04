import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "./api";
import "./Auth.css";

export default function ResetPassword() {
  const [params] = useSearchParams();
  const [status, setStatus] = useState("pending");
  const [error, setError] = useState("");
  const [newPassword, setNewPassword] = useState("");

  // Real flow: user must enter email and code manually
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [step, setStep] = useState(1); // Start at email entry
  const [message, setMessage] = useState("");

  const handleSendCode = async (e) => {
    e.preventDefault();
    setMessage("");
    try {
      await api("/auth/password-reset-request/", {
        method: "POST",
        body: { email },
      });
      setStep(2);
      setMessage("If the email exists, a reset code was sent.");
    } catch (err) {
      setMessage(err.message || "Request failed");
    }
  };

  const handleReset = async (e) => {
    e.preventDefault();
    setMessage("");
    try {
      await api("/auth/password-reset-confirm/", {
        method: "POST",
        body: { email, reset_code: code, new_password: password },
      });
      setStep(3);
    } catch (err) {
      setMessage(err.message || "Request failed");
    }
  };

  return (
    <div className="auth-container">
      <h2>Reset Password</h2>
      {step === 1 && (
        <form onSubmit={handleSendCode}>
          <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
          <button type="submit">Send Reset Code</button>
        </form>
      )}
      {step === 2 && (
        <form onSubmit={handleReset}>
          <input type="text" placeholder="Reset Code" value={code} onChange={e => setCode(e.target.value)} required />
          <input type="password" placeholder="New Password" value={password} onChange={e => setPassword(e.target.value)} required />
          <button type="submit">Reset Password</button>
        </form>
      )}
      {step === 3 && (
        <div>
          <p>{message}</p>
          <a href="/login">Go to Login</a>
        </div>
      )}
      {step !== 3 && message && <p>{message}</p>}
    </div>
  );
}

