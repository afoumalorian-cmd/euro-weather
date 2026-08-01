import {
  apiDelete,
  apiGet,
  apiPost,
} from "./apiClient";

const FAVORITES_PATH = "/api/weather/favorites/";

/**
 * Retrieve the favorite cities owned by the authenticated user.
 */
export function getFavoriteCities() {
  return apiGet(FAVORITES_PATH);
}

/**
 * Add a city to the authenticated user's favorites.
 */
export function createFavoriteCity({
  city,
  country,
  latitude,
  longitude,
}) {
  return apiPost(FAVORITES_PATH, {
    city,
    country,
    latitude,
    longitude,
  });
}

/**
 * Delete one favorite city owned by the authenticated user.
 */
export function deleteFavoriteCity(favoriteId) {
  return apiDelete(
    `${FAVORITES_PATH}${favoriteId}/`,
  );
}