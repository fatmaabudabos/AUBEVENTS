import React, { useState } from "react";
import "./Auth.css";
import { api } from "./api";

export default function ForgotPassword({ onSwitchLogin }) {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  // STEP 1: Send reset code
  const handleRequest = async (e) => {
    e.preventDefault();
    setError("");
    setMessage("");
    try {
      await api("/auth/password-reset-request/", {
        method: "POST",
        body: { email },
      });
      setMessage("A reset code has been sent to your email. Please enter it below.");
      setStep(2);
    } catch (err) {
      setError(err.message || "Error sending reset code.");
    }
  };

  // STEP 2: Reset password with code
  const handleReset = async (e) => {
    e.preventDefault();
    setError("");
    setMessage("");
    try {
      await api("/auth/password-reset-confirm/", {
        method: "POST",
        body: { email, reset_code: code, new_password: password },
      });
      setMessage("✅ Password reset successful! You can now log in.");
      setStep(3);
    } catch (err) {
      setError(err.message || "Error resetting password.");
    }
  };

  return (
    <div className="auth-container">
      <h2>Forgot Password</h2>

      {/* STEP 1: Request Code */}
      {step === 1 && (
        <form onSubmit={handleRequest}>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
            required
          />
          <button type="submit">Send Reset Code</button>
        </form>
      )}

      {/* STEP 2: Enter Code + New Password */}
      {step === 2 && (
        <form onSubmit={handleReset}>
          <input
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Enter the code you received"
            required
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter new password"
            required
          />
          <button type="submit">Reset Password</button>
        </form>
      )}

      {/* STEP 3: Success message */}
      {step === 3 && (
        <div>
          <p>{message}</p>
          <a href="/login">Go to Login</a>
        </div>
      )}

      {/* Flash messages */}
      {error && <div className="flash err">{error}</div>}

      {step !== 3 && (
        <p>
          Remembered?{" "}
          <button className="link" onClick={onSwitchLogin}>
            Back to Login
          </button>
        </p>
      )}
    </div>
  );
}
