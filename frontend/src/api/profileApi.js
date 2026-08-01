import {
  apiGet,
  apiPatch,
} from "./apiClient";

/**
 * Retrieve the authenticated user's profile.
 */
export function getUserProfile() {
  return apiGet("/api/auth/profile/");
}

/**
 * Update the authenticated user's profile.
 */
export function updateUserProfile({
  email,
  firstName,
  lastName,
}) {
  return apiPatch("/api/auth/profile/", {
    email,
    first_name: firstName,
    last_name: lastName,
  });
}