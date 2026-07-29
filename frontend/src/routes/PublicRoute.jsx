import { Navigate } from "react-router-dom";

function PublicRoute({ children }) {
  // Authenticated users should not return to login or registration.
  const accessToken = localStorage.getItem("accessToken");

  if (accessToken) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

export default PublicRoute;