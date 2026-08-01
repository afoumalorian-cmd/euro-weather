import {
  render,
  screen,
} from "@testing-library/react";
import {
  MemoryRouter,
  Route,
  Routes,
} from "react-router-dom";
import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import ProtectedRoute from "../routes/ProtectedRoute";

vi.mock("../api/tokenStorage", () => ({
  getAccessToken: vi.fn(),
}));

import { getAccessToken } from "../api/tokenStorage";

/**
 * Render the protected dashboard and login routes.
 */
function renderProtectedRoute() {
  return render(
    <MemoryRouter initialEntries={["/dashboard"]}>
      <Routes>
        <Route
          path="/login"
          element={<div>Login page</div>}
        />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <div>Protected dashboard</div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ProtectedRoute", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders protected content when an access token exists", () => {
    getAccessToken.mockReturnValue(
      "valid-access-token",
    );

    renderProtectedRoute();

    expect(
      screen.getByText("Protected dashboard"),
    ).toBeInTheDocument();

    expect(
      screen.queryByText("Login page"),
    ).not.toBeInTheDocument();
  });

  it("redirects to login when no access token exists", () => {
    getAccessToken.mockReturnValue(null);

    renderProtectedRoute();

    expect(
      screen.getByText("Login page"),
    ).toBeInTheDocument();

    expect(
      screen.queryByText("Protected dashboard"),
    ).not.toBeInTheDocument();
  });
});