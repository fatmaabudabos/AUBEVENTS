import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { api } from "./api";
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
  <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot" element={<ForgotPassword />} />
        <Route path="/reset/:token" element={<ResetPassword />} />
        <Route path="/verify/:token" element={<Verify />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/admin" element={<AdminRoute />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

function AdminRoute() {
  const [state, setState] = React.useState({ loading: true, allowed: false });
  React.useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const me = await api('/auth/me/', { method: 'GET', auth: true });
        if (!cancelled) setState({ loading: false, allowed: !!me?.is_admin });
      } catch {
        if (!cancelled) setState({ loading: false, allowed: false });
      }
    })();
    return () => { cancelled = true; };
  }, []);
  if (state.loading) return <div style={{ padding: 16 }}>Checking permissions…</div>;
  return state.allowed ? <AdminEventsPanel /> : <Navigate to="/login" replace />;
}
