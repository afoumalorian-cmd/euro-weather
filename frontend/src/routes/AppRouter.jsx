import {
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import DashboardPage from "../pages/DashboardPage";
import LoginPage from "../pages/LoginPage";
import RegisterPage from "../pages/RegisterPage";

function AppRouter() {
  return (
    <Routes>
      {/* Redirect the root URL to the login page. */}
      <Route path="/" element={<Navigate to="/login" replace />} />

      {/* Public authentication pages. */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Weather application dashboard. */}
      <Route path="/dashboard" element={<DashboardPage />} />

      {/* Redirect unknown URLs to the login page. */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default AppRouter;