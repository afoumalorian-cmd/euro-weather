import {
  Navigate,
  useLocation,
} from "react-router-dom";

import { getAccessToken } from "../api/tokenStorage";

function ProtectedRoute({ children }) {
  const location = useLocation();
  const accessToken = getAccessToken();

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