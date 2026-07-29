import { Navigate, useLocation } from "react-router-dom";

function ProtectedRoute({ children }) {
  const location = useLocation();

  // A dashboard route is accessible only when an access token exists.
  const accessToken = localStorage.getItem("accessToken");

  if (!accessToken) {
    return (
      <Navigate
        to="/login"
        replace
        state={{
          from: location.pathname,
          authenticationRequired: true,
        }}
      />
    );
  }

  return children;
}

export default ProtectedRoute;