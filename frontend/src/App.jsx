import { Routes, Route, Navigate } from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";
import Signup from "./pages/Signup";
import Login from "./pages/Login";
import Forgot from "./pages/Forgot";
import Dashboard from "./pages/Dashboard";
import Prediction from "./pages/Predictions/index.jsx";
import History from "./pages/History";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />

      <Route path="/login" element={<Login />} />
      <Route path="/Login" element={<Navigate to="/login" replace />} />

      <Route path="/signup" element={<Signup />} />
      <Route path="/Signup" element={<Navigate to="/signup" replace />} />

      <Route path="/forgot" element={<Forgot />} />
      <Route path="/Forgot" element={<Navigate to="/forgot" replace />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/Dashboard" element={<Navigate to="/dashboard" replace />} />
        <Route path="/prediction" element={<Prediction />} />
        <Route path="/find" element={<Prediction />} />
        <Route path="/history" element={<History />} />
        <Route path="/History" element={<Navigate to="/history" replace />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
