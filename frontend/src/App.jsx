import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Landing from "./Landing.jsx";
import Login from "./Login.jsx";
import Signup from "./Signup.jsx";
import ForgotPassword from "./ForgotPassword.jsx";
import ResetPassword from "./ResetPassword.jsx";
import Verify from "./Verify.jsx";
import Dashboard from "./Dashboard.jsx";
import AdminEventsPanel from "./admin/AdminEventsPanel.jsx";
import "./App.css";
import "./index.css";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<LoginRedirect />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot" element={<ForgotPassword />} />
        <Route path="/reset/:token" element={<ResetPassword />} />
        <Route path="/verify/:token" element={<Verify />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/admin" element={<AdminEventsPanel />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

// Temporary: all logins lead to admin panel
function LoginRedirect() {
  return <Navigate to="/admin" replace />;
}
