const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/**
 * Read a JSON response when possible.
 */
async function readResponsePayload(response) {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

/**
 * Extract a readable error message from a Django REST response.
 */
function extractErrorMessage(payload) {
  if (!payload) {
    return "The request could not be completed.";
  }

  if (typeof payload.error === "string") {
    return payload.error;
  }

  if (typeof payload.detail === "string") {
    return payload.detail;
  }

  const errors = payload.errors ?? payload;

  if (!errors || typeof errors !== "object") {
    return "The request could not be completed.";
  }

  for (const [field, value] of Object.entries(errors)) {
    if (Array.isArray(value) && value.length > 0) {
      return `${field}: ${value[0]}`;
    }

    if (typeof value === "string") {
      return `${field}: ${value}`;
    }
  }

  return "The request could not be completed.";
}

/**
 * Perform a JSON POST request against the backend.
 */
async function apiPost(path, body) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });
  } catch (error) {
    throw new Error(
      "The backend API cannot be reached. Check that Django is running.",
      { cause: error },
    );
  }

  const payload = await readResponsePayload(response);

  if (!response.ok) {
    throw new Error(extractErrorMessage(payload));
  }

  return payload;
}

/**
 * Create a new user account.
 */
export function registerUser({
  username,
  email,
  password,
  passwordConfirm,
}) {
  return apiPost("/api/auth/register/", {
    username,
    email,
    password,
    password_confirm: passwordConfirm,
  });
}

/**
 * Authenticate a user and retrieve JWT tokens.
 */
export function loginUser({
  username,
  password,
}) {
  return apiPost("/api/auth/login/", {
    username,
    password,
  });
}