import {
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import DashboardPage from "../pages/DashboardPage";
import LoginPage from "../pages/LoginPage";
import RegisterPage from "../pages/RegisterPage";
import WeatherHistoryPage from "../pages/WeatherHistoryPage";
import ProtectedRoute from "./ProtectedRoute";
import PublicRoute from "./PublicRoute";

function AppRouter() {
  return (
    <Routes>
      {/* Redirect the root URL according to authentication status. */}
      <Route
        path="/"
        element={<Navigate to="/dashboard" replace />}
      />

      {/* Public authentication pages. */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />

      <Route
        path="/register"
        element={
          <PublicRoute>
            <RegisterPage />
          </PublicRoute>
        }
      />

      {/* Protected weather dashboard. */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />

      {/* Protected historical weather page. */}
      <Route
        path="/history"
        element={
          <ProtectedRoute>
            <WeatherHistoryPage />
          </ProtectedRoute>
        }
      />

      {/* Redirect unknown URLs to the dashboard. */}
      <Route
        path="*"
        element={<Navigate to="/dashboard" replace />}
      />
    </Routes>
  );
}

export default AppRouter;