import {
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  ArrowLeft,
  CalendarDays,
  CheckCircle2,
  LoaderCircle,
  Mail,
  Save,
  Sun,
  User,
} from "lucide-react";
import {
  Link,
  useNavigate,
} from "react-router-dom";

import {
  getUserProfile,
  updateUserProfile,
} from "../api/profileApi";

/**
 * Format an ISO datetime using the browser locale.
 */
function formatDate(value) {
  if (!value) {
    return "Unavailable";
  }

  const parsedDate = new Date(value);

  if (Number.isNaN(parsedDate.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(parsedDate);
}

/**
 * Return initials used by the profile avatar.
 */
function getInitials({
  firstName,
  lastName,
  username,
}) {
  const initials = [
    firstName?.trim()?.charAt(0),
    lastName?.trim()?.charAt(0),
  ]
    .filter(Boolean)
    .join("")
    .toUpperCase();

  if (initials) {
    return initials;
  }

  return username?.trim()?.charAt(0)?.toUpperCase() || "U";
}

function UserProfilePage() {
  const navigate = useNavigate();

  const [profile, setProfile] = useState(null);

  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const initials = useMemo(
    () =>
      getInitials({
        firstName,
        lastName,
        username: profile?.username,
      }),
    [
      firstName,
      lastName,
      profile?.username,
    ],
  );

  /**
   * Load the authenticated user's profile.
   */
  async function loadProfile() {
    setLoading(true);
    setError("");

    try {
      const response = await getUserProfile();

      setProfile(response);
      setEmail(response.email ?? "");
      setFirstName(response.first_name ?? "");
      setLastName(response.last_name ?? "");
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The user profile could not be loaded.",
      );
    } finally {
      setLoading(false);
    }
  }

  /**
   * Update the authenticated user's editable information.
   */
  async function handleSubmit(event) {
    event.preventDefault();

    setSaving(true);
    setError("");
    setSuccessMessage("");

    try {
      const updatedProfile =
        await updateUserProfile({
          email: email.trim(),
          firstName: firstName.trim(),
          lastName: lastName.trim(),
        });

      setProfile(updatedProfile);
      setEmail(updatedProfile.email ?? "");
      setFirstName(updatedProfile.first_name ?? "");
      setLastName(updatedProfile.last_name ?? "");

      localStorage.setItem(
        "username",
        updatedProfile.username,
      );

      setSuccessMessage(
        "Your profile has been updated successfully.",
      );
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The user profile could not be updated.",
      );
    } finally {
      setSaving(false);
    }
  }

  useEffect(() => {
    loadProfile();
  }, []);

  return (
    <div className="profile-page">
      <div
        className="ambient-background"
        aria-hidden="true"
      >
        <div className="ambient-orb ambient-orb-one" />
        <div className="ambient-orb ambient-orb-two" />
        <div className="ambient-grid" />
      </div>

      <header className="profile-page-header">
        <Link
          className="dashboard-brand"
          to="/dashboard"
        >
          <span className="brand-icon">
            <Sun size={22} />
          </span>

          <span>
            Euro <strong>Weather</strong>
          </span>
        </Link>

        <button
          className="profile-back-button"
          type="button"
          onClick={() => navigate("/dashboard")}
        >
          <ArrowLeft size={18} />
          Back to dashboard
        </button>
      </header>

      <main className="profile-page-container">
        <section className="profile-page-introduction">
          <div>
            <p className="eyebrow">
              Account settings
            </p>

            <h1>Your profile</h1>

            <p>
              Manage your personal information and review
              your Euro Weather account details.
            </p>
          </div>
        </section>

        {error ? (
          <div
            className="dashboard-error"
            role="alert"
          >
            <strong>Unable to complete the request</strong>
            <span>{error}</span>
          </div>
        ) : null}

        {successMessage ? (
          <div
            className="profile-success-message"
            role="status"
          >
            <CheckCircle2 size={20} />

            <span>{successMessage}</span>
          </div>
        ) : null}

        {loading ? (
          <section className="profile-loading-card">
            <LoaderCircle
              className="loading-spinner"
              size={28}
            />

            <span>Loading your profile...</span>
          </section>
        ) : profile ? (
          <section className="profile-layout">
            <aside className="profile-summary-card">
              <div className="profile-large-avatar">
                {initials}
              </div>

              <div>
                <h2>
                  {firstName || lastName
                    ? `${firstName} ${lastName}`.trim()
                    : profile.username}
                </h2>

                <p>@{profile.username}</p>
              </div>

              <div className="profile-summary-details">
                <div>
                  <User size={18} />

                  <span>
                    <small>Username</small>
                    <strong>{profile.username}</strong>
                  </span>
                </div>

                <div>
                  <Mail size={18} />

                  <span>
                    <small>Email</small>
                    <strong>
                      {email || "Not provided"}
                    </strong>
                  </span>
                </div>

                <div>
                  <CalendarDays size={18} />

                  <span>
                    <small>Member since</small>
                    <strong>
                      {formatDate(profile.date_joined)}
                    </strong>
                  </span>
                </div>
              </div>
            </aside>

            <form
              className="profile-form-card"
              onSubmit={handleSubmit}
            >
              <div className="profile-form-header">
                <div>
                  <p className="eyebrow">
                    Personal information
                  </p>

                  <h2>Edit profile</h2>
                </div>
              </div>

              <div className="profile-form-grid">
                <label>
                  <span>Username</span>

                  <input
                    type="text"
                    value={profile.username}
                    disabled
                  />

                  <small>
                    Your username cannot be changed.
                  </small>
                </label>

                <label>
                  <span>Email address</span>

                  <input
                    type="email"
                    value={email}
                    required
                    autoComplete="email"
                    onChange={(event) =>
                      setEmail(event.target.value)
                    }
                  />
                </label>

                <label>
                  <span>First name</span>

                  <input
                    type="text"
                    value={firstName}
                    autoComplete="given-name"
                    placeholder="Enter your first name"
                    onChange={(event) =>
                      setFirstName(event.target.value)
                    }
                  />
                </label>

                <label>
                  <span>Last name</span>

                  <input
                    type="text"
                    value={lastName}
                    autoComplete="family-name"
                    placeholder="Enter your last name"
                    onChange={(event) =>
                      setLastName(event.target.value)
                    }
                  />
                </label>
              </div>

              <div className="profile-form-actions">
                <button
                  className="profile-cancel-button"
                  type="button"
                  disabled={saving}
                  onClick={() => navigate("/dashboard")}
                >
                  Cancel
                </button>

                <button
                  className="profile-save-button"
                  type="submit"
                  disabled={saving}
                >
                  {saving ? (
                    <>
                      <LoaderCircle
                        className="loading-spinner"
                        size={18}
                      />
                      Saving
                    </>
                  ) : (
                    <>
                      <Save size={18} />
                      Save changes
                    </>
                  )}
                </button>
              </div>
            </form>
          </section>
        ) : null}
      </main>
    </div>
  );
}

export default UserProfilePage;