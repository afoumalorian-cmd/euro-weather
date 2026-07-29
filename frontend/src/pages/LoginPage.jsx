import { useState } from "react";
import {
  Link,
  useLocation,
  useNavigate,
} from "react-router-dom";
import {
  ArrowRight,
  CheckCircle2,
  CloudSun,
  Eye,
  EyeOff,
  LoaderCircle,
  LockKeyhole,
  UserRound
} from "lucide-react";

import { loginUser } from "../api/authApi";

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const registrationUsername =
    location.state?.username ?? "";

  const [formData, setFormData] = useState({
    username: registrationUsername,
    password: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  const registrationSuccess =
    location.state?.registrationSuccess === true;

  /**
   * Update one login field while preserving the other value.
   */
  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((currentData) => ({
      ...currentData,
      [name]: value,
    }));

    if (error) {
      setError("");
    }
  }

  /**
   * Authenticate the user and store the JWT tokens locally.
   */
  async function handleSubmit(event) {
    event.preventDefault();

    const username = formData.username.trim();
    const password = formData.password;

    if (!username || !password) {
      setError("Please enter your username and password.");
      return;
    }
  
    setIsSubmitting(true);
    setError("");

    try {
      const response = await loginUser({
        username,
        password,
      });

      /*
       * Support both a direct SimpleJWT response and a response
       * where tokens are nested inside a data property.
       */
      const accessToken =
        response?.access ??
        response?.data?.access ??
        response?.tokens?.access;

      const refreshToken =
        response?.refresh ??
        response?.data?.refresh ??
        response?.tokens?.refresh;

      if (!accessToken || !refreshToken) {
        throw new Error(
          "The backend did not return valid authentication tokens.",
        );
      }

      localStorage.setItem("accessToken", accessToken);
      localStorage.setItem("refreshToken", refreshToken);
      // Store the username to personalize the dashboard.
      localStorage.setItem("username", username);

      navigate("/dashboard", {
        replace: true,
      });
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Authentication failed.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="auth-page auth-page-premium">
      <div className="auth-ambient" aria-hidden="true">
        <div className="auth-orb auth-orb-primary" />
        <div className="auth-orb auth-orb-secondary" />
        <div className="auth-grid-pattern" />
      </div>

      <section className="auth-showcase">
        <div className="auth-showcase-content">
          <Link className="auth-logo" to="/">
            <span className="auth-logo-icon">
              <CloudSun size={25} />
            </span>

            <span>
              Euro <strong>Weather</strong>
            </span>
          </Link>

          <div className="auth-showcase-copy">
            <p className="auth-eyebrow">
              Reliable weather intelligence
            </p>

            <h1>
              Plan smarter with a clear view of the weather.
            </h1>

            <p>
              Search European cities and explore current, future,
              hourly, and historical weather from one dashboard.
            </p>
          </div>

          <div className="auth-weather-preview">
            <div>
              <span>Paris</span>
              <strong>24°C</strong>
            </div>

            <div className="auth-preview-icon">
              ☀️
            </div>

            <div>
              <span>Clear conditions</span>
              <small>Feels like 25°C</small>
            </div>
          </div>
        </div>
      </section>

      <section className="auth-form-section">
        <div className="auth-card auth-card-premium">
          <div className="auth-header">
            <p className="brand-name">
              Welcome back
            </p>

            <h2>
              Sign in to continue
            </h2>

            <p>
              Access your weather dashboard and continue exploring.
            </p>
          </div>

          {registrationSuccess ? (
            <div className="auth-message auth-message-success">
              <CheckCircle2 size={19} />

              <div>
                <strong>Account created successfully</strong>
                <span>You can now sign in.</span>
              </div>
            </div>
          ) : null}

          {error ? (
            <div className="auth-message auth-message-error" role="alert">
              <strong>Sign-in failed</strong>
              <span>{error}</span>
            </div>
          ) : null}

          <form
            className="auth-form"
            onSubmit={handleSubmit}
            noValidate
          >
            <label htmlFor="username">
              Username

              <div className="auth-input-wrapper">
                <UserRound size={18} />

                <input
                  id="username"
                  name="username"
                  type="text"
                  value={formData.username}
                  placeholder="Enter your username"
                  autoComplete="username"
                  required
                  disabled={isSubmitting}
                  onChange={handleChange}
                />
              </div>
            </label>

            <label htmlFor="password">
              Password

              <div className="auth-input-wrapper">
                <LockKeyhole size={18} />

                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  value={formData.password}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  required
                  disabled={isSubmitting}
                  onChange={handleChange}
                />

                <button
                  className="password-visibility-button"
                  type="button"
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                  onClick={() => setShowPassword((current) => !current)}
                >
                  {showPassword ? (
                    <EyeOff size={18} />
                  ) : (
                    <Eye size={18} />
                  )}
                </button>
              </div>
            </label>

            <div className="auth-form-options">
              <label className="remember-me-option">
                <input type="checkbox" />
                Remember me
              </label>

              <button
                className="forgot-password-button"
                type="button"
              >
                Forgot password?
              </button>
            </div>

            <button
              className="auth-submit-button"
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <LoaderCircle
                    className="loading-spinner"
                    size={19}
                  />
                  Signing in...
                </>
              ) : (
                <>
                  Sign in
                  <ArrowRight size={19} />
                </>
              )}
            </button>
          </form>

          <p className="auth-footer">
            Don&apos;t have an account?{" "}
            <Link to="/register">
              Create an account
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}

export default LoginPage;