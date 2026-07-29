const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/**
 * Convert an object into URL query parameters.
 */
function buildQueryString(parameters) {
  const searchParameters = new URLSearchParams();

  Object.entries(parameters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParameters.set(key, String(value));
    }
  });

  return searchParameters.toString();
}

/**
 * Perform a GET request against the Django API.
 */
async function apiGet(path, parameters = {}) {
  const queryString = buildQueryString(parameters);
  const url = `${API_BASE_URL}${path}${
    queryString ? `?${queryString}` : ""
  }`;

  let response;

  try {
    response = await fetch(url, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    });
  } catch (error) {
    throw new Error(
      "The backend API cannot be reached. Check that Django is running.",
      { cause: error },
    );
  }

  let payload;

  try {
    payload = await response.json();
  } catch {
    throw new Error("The backend returned an invalid JSON response.");
  }

  if (!response.ok) {
    const errorMessage =
      payload.error ??
      extractValidationError(payload.errors) ??
      "The request could not be completed.";

    throw new Error(errorMessage);
  }

  return payload;
}

/**
 * Extract the first readable validation error returned by Django REST Framework.
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

  if (firstValue && typeof firstValue === "object") {
    return extractValidationError(firstValue);
  }

  return null;
}

/**
 * Retrieve the daily forecast and resolved location.
 */
export function getDailyForecastByCity({
  city,
  country,
  days = 7,
}) {
  return apiGet("/api/weather/forecast/daily/by-city/", {
    city,
    country,
    days,
  });
}

/**
 * Retrieve the current weather using geographic coordinates.
 */
export function getCurrentWeather({
  latitude,
  longitude,
}) {
  return apiGet("/api/weather/current/", {
    latitude,
    longitude,
  });
}

/**
 * Retrieve all hourly forecasts for one selected date.
 */
export function getHourlyForecastByCity({
  city,
  country,
  forecastDate,
}) {
  return apiGet("/api/weather/forecast/hourly/by-city/", {
    city,
    country,
    forecast_date: forecastDate,
  });
}

/**
 * Retrieve historical weather data for a selected date range.
 */
export function getHistoricalWeatherByCity({
  city,
  country,
  startDate,
  endDate,
}) {
  return apiGet("/api/weather/history/by-city/", {
    city,
    country,
    start_date: startDate,
    end_date: endDate,
  });
}