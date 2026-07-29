import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ArrowRight,
  CheckCircle2,
  CloudSun,
  Eye,
  EyeOff,
  LoaderCircle,
  LockKeyhole,
  Mail,
  UserRound,
} from "lucide-react";

import { registerUser } from "../api/authApi";

function RegisterPage() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    passwordConfirm: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  /**
   * Update one form field without replacing the other values.
   */
  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((currentData) => ({
      ...currentData,
      [name]: value,
    }));

    // Remove the previous error as soon as the user edits the form.
    if (error) {
      setError("");
    }
  }

  /**
   * Create the account through the Django registration endpoint.
   */
  async function handleSubmit(event) {
    event.preventDefault();

    const username = formData.username.trim();
    const email = formData.email.trim();
    const password = formData.password;
    const passwordConfirm = formData.passwordConfirm;

    if (!username || !email || !password || !passwordConfirm) {
      setError("Please complete all required fields.");
      return;
    }

    if (password !== passwordConfirm) {
      setError("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);
    setError("");

    try {
      await registerUser({
        username,
        email,
        password,
        passwordConfirm,
      });

      /*
       * Redirect to login after successful registration.
       * The state message will be displayed by LoginPage.
       */
      navigate("/login", {
        replace: true,
        state: {
          registrationSuccess: true,
          username,
        },
      });
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The account could not be created.",
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
              Your European weather companion
            </p>

            <h1>
              Discover the weather before it shapes your day.
            </h1>

            <p>
              Access current conditions, precise hourly forecasts,
              extended daily outlooks, and historical weather data.
            </p>
          </div>

          <div className="auth-benefits">
            <div>
              <CheckCircle2 size={18} />
              <span>Real-time weather conditions</span>
            </div>

            <div>
              <CheckCircle2 size={18} />
              <span>Hourly and daily forecasts</span>
            </div>

            <div>
              <CheckCircle2 size={18} />
              <span>Historical weather exploration</span>
            </div>
          </div>
        </div>
      </section>

      <section className="auth-form-section">
        <div className="auth-card auth-card-premium">
          <div className="auth-header">
            <p className="brand-name">
              Create your account
            </p>

            <h2>
              Start exploring
            </h2>

            <p>
              Create an account to access your personal weather dashboard.
            </p>
          </div>

          {error ? (
            <div className="auth-message auth-message-error" role="alert">
              <strong>Registration failed</strong>
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
                  placeholder="Choose a username"
                  autoComplete="username"
                  minLength={3}
                  required
                  disabled={isSubmitting}
                  onChange={handleChange}
                />
              </div>
            </label>

            <label htmlFor="email">
              Email address

              <div className="auth-input-wrapper">
                <Mail size={18} />

                <input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  placeholder="name@example.com"
                  autoComplete="email"
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
                  placeholder="Create a secure password"
                  autoComplete="new-password"
                  minLength={8}
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

            <label htmlFor="passwordConfirm">
              Confirm password

              <div className="auth-input-wrapper">
                <LockKeyhole size={18} />

                <input
                  id="passwordConfirm"
                  name="passwordConfirm"
                  type={showPassword ? "text" : "password"}
                  value={formData.passwordConfirm}
                  placeholder="Confirm your password"
                  autoComplete="new-password"
                  minLength={8}
                  required
                  disabled={isSubmitting}
                  onChange={handleChange}
                />
              </div>
            </label>

            <div className="password-requirement">
              Use at least 8 characters with a secure combination.
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
                  Creating account...
                </>
              ) : (
                <>
                  Create account
                  <ArrowRight size={19} />
                </>
              )}
            </button>
          </form>

          <p className="auth-footer">
            Already have an account?{" "}
            <Link to="/login">
              Sign in
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}

export default RegisterPage;