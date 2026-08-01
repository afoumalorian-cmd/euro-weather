import {
  clearAuthentication,
  getAccessToken,
  getRefreshToken,
  storeAccessToken,
} from "./tokenStorage";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  "http://localhost:8000";

const REFRESH_TOKEN_PATH =
  import.meta.env.VITE_AUTH_REFRESH_PATH ??
  "/api/auth/token/refresh/";

let refreshRequestPromise = null;

/**
 * Convert an object into URL query parameters.
 */
function buildQueryString(parameters) {
  const searchParameters = new URLSearchParams();

  Object.entries(parameters).forEach(([key, value]) => {
    if (
      value !== undefined &&
      value !== null &&
      value !== ""
    ) {
      searchParameters.set(key, String(value));
    }
  });

  return searchParameters.toString();
}

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
 * Extract the first readable validation error.
 */
function extractValidationError(errors) {
  if (!errors || typeof errors !== "object") {
    return null;
  }

  const firstValue = Object.values(errors)[0];

  if (Array.isArray(firstValue)) {
    return String(firstValue[0]);
  }

  if (typeof firstValue === "string") {
    return firstValue;
  }

  if (
    firstValue &&
    typeof firstValue === "object"
  ) {
    return extractValidationError(firstValue);
  }

  return null;
}

/**
 * Extract a readable error message from the backend payload.
 */
/**
 * Extract a readable error message from the backend payload.
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

  return (
    extractValidationError(payload.errors) ??
    extractValidationError(payload) ??
    "The request could not be completed."
  );
}

/**
 * Redirect the user to the login page after authentication failure.
 */
function redirectToLogin() {
  clearAuthentication();

  if (window.location.pathname !== "/login") {
    window.location.replace("/login");
  }
}

/**
 * Request a new access token using the stored refresh token.
 */
async function requestNewAccessToken() {
  const refreshToken = getRefreshToken();

  if (!refreshToken) {
    throw new Error("No refresh token is available.");
  }

  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}${REFRESH_TOKEN_PATH}`,
      {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          refresh: refreshToken,
        }),
      },
    );
  } catch (error) {
    throw new Error(
      "The authentication service cannot be reached.",
      { cause: error },
    );
  }

  const payload = await readResponsePayload(response);

  if (!response.ok) {
    throw new Error(
      extractErrorMessage(payload),
    );
  }

  const newAccessToken =
    payload?.access ??
    payload?.access_token ??
    payload?.accessToken;

  if (!newAccessToken) {
    throw new Error(
      "The backend did not return a new access token.",
    );
  }

  storeAccessToken(newAccessToken);

  return newAccessToken;
}

/**
 * Refresh the access token while preventing duplicate refresh requests.
 */
async function refreshAccessToken() {
  if (!refreshRequestPromise) {
    refreshRequestPromise = requestNewAccessToken()
      .finally(() => {
        refreshRequestPromise = null;
      });
  }

  return refreshRequestPromise;
}

/**
 * Perform an authenticated request against the Django API.
 */
async function authenticatedFetch(
  url,
  options = {},
  allowRetry = true,
) {
  const accessToken = getAccessToken();

  const headers = new Headers(options.headers);

  headers.set("Accept", "application/json");

  if (accessToken) {
    headers.set(
      "Authorization",
      `Bearer ${accessToken}`,
    );
  }

  let response;

  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch (error) {
    throw new Error(
      "The backend API cannot be reached. Check that Django is running.",
      { cause: error },
    );
  }

  if (response.status !== 401 || !allowRetry) {
    return response;
  }

  try {
    const newAccessToken =
      await refreshAccessToken();

    headers.set(
      "Authorization",
      `Bearer ${newAccessToken}`,
    );

    return await fetch(url, {
      ...options,
      headers,
    });
  } catch {
    redirectToLogin();

    throw new Error(
      "Your session has expired. Please sign in again.",
    );
  }
}

/**
 * Perform an authenticated GET request.
 */
export async function apiGet(
  path,
  parameters = {},
) {
  const queryString =
    buildQueryString(parameters);

  const url = `${API_BASE_URL}${path}${
    queryString ? `?${queryString}` : ""
  }`;

  const response = await authenticatedFetch(url, {
    method: "GET",
  });

  const payload =
    await readResponsePayload(response);

  if (!response.ok) {
    throw new Error(
      extractErrorMessage(payload),
    );
  }

  return payload;
}

/**
 * Perform an authenticated JSON POST request.
 */
export async function apiPost(
  path,
  body,
) {
  const url = `${API_BASE_URL}${path}`;

  const response = await authenticatedFetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const payload =
    await readResponsePayload(response);

  if (!response.ok) {
    throw new Error(
      extractErrorMessage(payload),
    );
  }

  return payload;
}

/**
 * Perform an authenticated DELETE request.
 */
export async function apiDelete(path) {
  const url = `${API_BASE_URL}${path}`;

  const response = await authenticatedFetch(url, {
    method: "DELETE",
  });

  /*
   * A successful DELETE commonly returns 204 No Content,
   * so there may be no JSON payload to read.
   */
  const payload =
    response.status === 204
      ? null
      : await readResponsePayload(response);

  if (!response.ok) {
    throw new Error(
      extractErrorMessage(payload),
    );
  }

  return payload;
}