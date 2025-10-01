



import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./Login";
import Signup from "./Signup";
import ForgotPassword from "./ForgotPassword";
import Landing from "./Landing";
import Dashboard from "./Dashboard";
import Verify from "./Verify";
import ResetPassword from "./ResetPassword";
import "./App.css";


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login onSwitch={() => window.location.href = '/signup'} onForgot={() => window.location.href = '/forgot'} />} />
        <Route path="/signup" element={<Signup onSwitch={() => window.location.href = '/login'} />} />
        <Route path="/forgot" element={<ForgotPassword onSwitchLogin={() => window.location.href = '/login'} />} />
        <Route path="/verify" element={<Verify />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
