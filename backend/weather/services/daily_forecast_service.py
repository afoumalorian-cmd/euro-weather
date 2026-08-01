import logging
from typing import Any

import requests


logger = logging.getLogger(__name__)

class DailyForecastServiceError(Exception):
    """
    Base exception raised when the daily forecast service
    cannot return valid weather data.
    """


class DailyForecastServiceUnavailableError(DailyForecastServiceError):
    """
    Exception raised when the Open-Meteo API is unavailable
    or does not respond before the timeout.
    """


class DailyForecastService:
    """
    Retrieve and normalize daily weather forecasts
    from the Open-Meteo Forecast API.
    """

    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    REQUEST_TIMEOUT = 10

    DAILY_VARIABLES = [
        "weather_code",
        "temperature_2m_max",
        "temperature_2m_min",
        "apparent_temperature_max",
        "apparent_temperature_min",
        "sunrise",
        "sunset",
        "precipitation_sum",
        "rain_sum",
        "showers_sum",
        "snowfall_sum",
        "precipitation_hours",
        "precipitation_probability_max",
        "wind_speed_10m_max",
        "wind_gusts_10m_max",
        "wind_direction_10m_dominant",
    ]

    @classmethod
    def get_daily_forecast(
        cls,
        latitude: float,
        longitude: float,
        days: int = 7,
    ) -> dict[str, Any]:
        """
        Retrieve a daily weather forecast for the provided coordinates.

        Args:
            latitude:
                Latitude between -90 and 90.

            longitude:
                Longitude between -180 and 180.

            days:
                Number of forecast days between 1 and 16.

        Returns:
            A normalized dictionary containing the location,
            daily forecasts, and measurement units.

        Raises:
            DailyForecastServiceUnavailableError:
                When Open-Meteo cannot be reached.

            DailyForecastServiceError:
                When Open-Meteo returns invalid or incomplete data.
        """

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": ",".join(cls.DAILY_VARIABLES),
            "forecast_days": days,

            # Resolve the local timezone from the coordinates.
            # Daily values require a timezone so dates are locally accurate.
            "timezone": "auto",
        }

        try:
            response = requests.get(
                cls.BASE_URL,
                params=params,
                timeout=cls.REQUEST_TIMEOUT,
            )

            response.raise_for_status()

        except requests.Timeout as exc:
            raise DailyForecastServiceUnavailableError(
                "The forecast service did not respond in time."
            ) from exc

        except requests.ConnectionError as exc:
            raise DailyForecastServiceUnavailableError(
                "The forecast service is currently unavailable."
            ) from exc

        except requests.HTTPError as exc:
            upstream_response = exc.response

            logger.error(
                "Open-Meteo daily forecast request failed. "
                "status_code=%s url=%s response=%s",
                (
                    upstream_response.status_code
                    if upstream_response is not None
                    else "unknown"
                ),
                (
                    upstream_response.url
                    if upstream_response is not None
                    else cls.BASE_URL
                ),
                (
                    upstream_response.text[:1000]
                    if upstream_response is not None
                    else "No response body."
                ),
            )

            raise DailyForecastServiceError(
                "The forecast service returned an HTTP error."
            ) from exc

        except requests.RequestException as exc:
            raise DailyForecastServiceError(
                "An unexpected error occurred while contacting "
                "the forecast service."
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise DailyForecastServiceError(
                "The forecast service returned invalid JSON."
            ) from exc

        daily = payload.get("daily")
        daily_units = payload.get("daily_units")

        if not isinstance(daily, dict):
            raise DailyForecastServiceError(
                "The forecast service returned invalid daily data."
            )

        if not isinstance(daily_units, dict):
            daily_units = {}

        return cls._normalize_response(
            payload=payload,
            daily=daily,
            daily_units=daily_units,
        )

    @classmethod
    def _normalize_response(
        cls,
        payload: dict[str, Any],
        daily: dict[str, Any],
        daily_units: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Convert parallel Open-Meteo arrays into a list
        containing one normalized object per forecast day.
        """

        dates = daily.get("time")

        if not isinstance(dates, list):
            raise DailyForecastServiceError(
                "The forecast service returned invalid forecast dates."
            )

        forecasts = []

        for index, date in enumerate(dates):
            forecasts.append(
                {
                    "date": date,
                    "weather_code": cls._get_value(
                        daily,
                        "weather_code",
                        index,
                    ),
                    "temperature_max": cls._get_value(
                        daily,
                        "temperature_2m_max",
                        index,
                    ),
                    "temperature_min": cls._get_value(
                        daily,
                        "temperature_2m_min",
                        index,
                    ),
                    "apparent_temperature_max": cls._get_value(
                        daily,
                        "apparent_temperature_max",
                        index,
                    ),
                    "apparent_temperature_min": cls._get_value(
                        daily,
                        "apparent_temperature_min",
                        index,
                    ),
                    "sunrise": cls._get_value(
                        daily,
                        "sunrise",
                        index,
                    ),
                    "sunset": cls._get_value(
                        daily,
                        "sunset",
                        index,
                    ),
                    "precipitation_sum": cls._get_value(
                        daily,
                        "precipitation_sum",
                        index,
                    ),
                    "rain_sum": cls._get_value(
                        daily,
                        "rain_sum",
                        index,
                    ),
                    "showers_sum": cls._get_value(
                        daily,
                        "showers_sum",
                        index,
                    ),
                    "snowfall_sum": cls._get_value(
                        daily,
                        "snowfall_sum",
                        index,
                    ),
                    "precipitation_hours": cls._get_value(
                        daily,
                        "precipitation_hours",
                        index,
                    ),
                    "precipitation_probability_max": cls._get_value(
                        daily,
                        "precipitation_probability_max",
                        index,
                    ),
                    "wind_speed_max": cls._get_value(
                        daily,
                        "wind_speed_10m_max",
                        index,
                    ),
                    "wind_gusts_max": cls._get_value(
                        daily,
                        "wind_gusts_10m_max",
                        index,
                    ),
                    "wind_direction_dominant": cls._get_value(
                        daily,
                        "wind_direction_10m_dominant",
                        index,
                    ),
                }
            )

        return {
            "location": {
                "latitude": payload.get("latitude"),
                "longitude": payload.get("longitude"),
                "elevation": payload.get("elevation"),
                "timezone": payload.get("timezone"),
                "timezone_abbreviation": payload.get(
                    "timezone_abbreviation"
                ),
                "utc_offset_seconds": payload.get("utc_offset_seconds"),
            },
            "daily": forecasts,
            "units": {
                "weather_code": daily_units.get("weather_code"),
                "temperature_max": daily_units.get(
                    "temperature_2m_max"
                ),
                "temperature_min": daily_units.get(
                    "temperature_2m_min"
                ),
                "apparent_temperature_max": daily_units.get(
                    "apparent_temperature_max"
                ),
                "apparent_temperature_min": daily_units.get(
                    "apparent_temperature_min"
                ),
                "sunrise": daily_units.get("sunrise"),
                "sunset": daily_units.get("sunset"),
                "precipitation_sum": daily_units.get(
                    "precipitation_sum"
                ),
                "rain_sum": daily_units.get("rain_sum"),
                "showers_sum": daily_units.get("showers_sum"),
                "snowfall_sum": daily_units.get("snowfall_sum"),
                "precipitation_hours": daily_units.get(
                    "precipitation_hours"
                ),
                "precipitation_probability_max": daily_units.get(
                    "precipitation_probability_max"
                ),
                "wind_speed_max": daily_units.get(
                    "wind_speed_10m_max"
                ),
                "wind_gusts_max": daily_units.get(
                    "wind_gusts_10m_max"
                ),
                "wind_direction_dominant": daily_units.get(
                    "wind_direction_10m_dominant"
                ),
            },
        }

    @staticmethod
    def _get_value(
        data: dict[str, Any],
        key: str,
        index: int,
    ) -> Any:
        """
        Safely retrieve a value from one of Open-Meteo's
        parallel daily data arrays.
        """

        values = data.get(key)

        if not isinstance(values, list):
            return None

        if index >= len(values):
            return None

        return values[index]