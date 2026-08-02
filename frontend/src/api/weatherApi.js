import { apiGet } from "./apiClient";

/**
 * Retrieve the daily forecast and resolved location.
 */
export function getDailyForecastByCity({
  city,
  country,
  days = 7,
}) {
  return apiGet(
    "/api/weather/forecast/daily/by-city/",
    {
      city,
      country,
      days,
    },
  );
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
 * Retrieve the daily forecast using geographic coordinates.
 */
export function getDailyForecast({
  latitude,
  longitude,
  days = 7,
}) {
  return apiGet(
    "/api/weather/forecast/daily/",
    {
      latitude,
      longitude,
      days,
    },
  );
}

/**
 * Retrieve all hourly forecasts for one selected date.
 */
export function getHourlyForecastByCity({
  city,
  country,
  forecastDate,
}) {
  return apiGet(
    "/api/weather/forecast/hourly/by-city/",
    {
      city,
      country,
      forecast_date: forecastDate,
    },
  );
}

/**
 * Retrieve the hourly forecast using geographic coordinates.
 */
export function getHourlyForecast({
  latitude,
  longitude,
  forecastDate,
}) {
  return apiGet(
    "/api/weather/forecast/hourly/",
    {
      latitude,
      longitude,
      forecast_date: forecastDate,
    },
  );
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
  return apiGet(
    "/api/weather/history/by-city/",
    {
      city,
      country,
      start_date: startDate,
      end_date: endDate,
    },
  );
}

/**
 * Resolve geographic coordinates into a readable location.
 */
export function reverseGeocode({
  latitude,
  longitude,
}) {
  return apiGet(
    "/api/weather/locations/reverse/",
    {
      latitude,
      longitude,
    },
  );
}