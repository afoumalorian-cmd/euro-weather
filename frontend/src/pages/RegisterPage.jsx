import { Link } from "react-router-dom";

function RegisterPage() {
  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-header">
          <p className="brand-name">Euro Weather</p>
          <h1>Create your account</h1>
          <p>Register to access weather forecasts and history.</p>
        </div>

        <form className="auth-form">
          <label htmlFor="username">
            Username
            <input
              id="username"
              name="username"
              type="text"
              placeholder="Choose a username"
              autoComplete="username"
              required
            />
          </label>

          <label htmlFor="email">
            Email
            <input
              id="email"
              name="email"
              type="email"
              placeholder="name@example.com"
              autoComplete="email"
              required
            />
          </label>

          <label htmlFor="password">
            Password
            <input
              id="password"
              name="password"
              type="password"
              placeholder="Create a password"
              autoComplete="new-password"
              required
            />
          </label>

          <button type="submit">Create account</button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </section>
    </main>
  );
}

export default RegisterPage;