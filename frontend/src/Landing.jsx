import React from "react";
import { useNavigate } from "react-router-dom";
import "./Landing.css";

export default function Landing() {
  const navigate = useNavigate();
  return (
    <div className="landing-container">
      <div className="landing-content">
        <h1 className="aub-title landing-title">AUBEVENTS</h1>
        <p className="landing-desc">
          Discover and join events happening at AUB — from workshops and lectures to concerts and club fairs.<br/>
          <span className="aub-tagline">Your hub for student events at AUB.</span>
        </p>
        <div className="landing-actions">
          <button className="landing-btn" onClick={() => navigate("/signup")}>Sign Up</button>
          <button className="landing-btn secondary" onClick={() => navigate("/login")}>Log In</button>
        </div>
      </div>
    </div>
  );
}
