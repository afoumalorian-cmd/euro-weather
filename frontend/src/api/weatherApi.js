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