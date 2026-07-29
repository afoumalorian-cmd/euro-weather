import { Link } from "react-router-dom";

function LoginPage() {
  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-header">
          <p className="brand-name">Euro Weather</p>
          <h1>Welcome back</h1>
          <p>Sign in to access your weather dashboard.</p>
        </div>

        <form className="auth-form">
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
              placeholder="Enter your password"
              autoComplete="current-password"
              required
            />
          </label>

          <button type="submit">Sign in</button>
        </form>

        <p className="auth-footer">
          Don&apos;t have an account?{" "}
          <Link to="/register">Create an account</Link>
        </p>
      </section>
    </main>
  );
}

export default LoginPage;