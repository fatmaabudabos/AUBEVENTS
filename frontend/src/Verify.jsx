import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "./api";
import "./Auth.css";

export default function Verify() {
  const [params] = useSearchParams();
  const [status, setStatus] = useState("pending");
  const [error, setError] = useState("");

  useEffect(() => {
    const email = params.get("email");
    const token = params.get("token");
    if (!email || !token) {
      setStatus("error");
      setError("Invalid verification link.");
      return;
    }
    api("/auth/verify/", {
      method: "POST",
      body: { email, token },
    })
      .then(() => setStatus("success"))
      .catch((err) => {
        setStatus("error");
        setError(err.message);
      });
  }, [params]);

  if (status === "pending") return <div className="auth-container"><h2>Verifying...</h2></div>;
  if (status === "success")
    return (
      <div className="auth-container">
        <h2>Account Verified!</h2>
        <p>Your account has been verified. You can now <a href="/login">log in</a>.</p>
      </div>
    );
  return (
    <div className="auth-container">
      <h2>Verification Failed</h2>
      <p className="flash err">{error}</p>
      <a href="/signup">Back to Sign Up</a>
    </div>
  );
}
