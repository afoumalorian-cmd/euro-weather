from typing import Any

import requests


class HourlyForecastServiceError(Exception):
    """
    Base exception raised when the hourly forecast service
    cannot return valid weather data.
    """


class HourlyForecastServiceUnavailableError(HourlyForecastServiceError):
    """
    Exception raised when the Open-Meteo API is unavailable
    or does not respond before the timeout.
    """


class HourlyForecastService:
    """
    Retrieve and normalize hourly weather forecasts
    from the Open-Meteo Forecast API.
    """

    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    REQUEST_TIMEOUT = 10

    HOURLY_VARIABLES = [
        "temperature_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "precipitation_probability",
        "precipitation",
        "rain",
        "showers",
        "snowfall",
        "weather_code",
        "cloud_cover",
        "visibility",
        "wind_speed_10m",
        "wind_direction_10m",
        "wind_gusts_10m",
        "is_day",
    ]

    @classmethod
    def get_hourly_forecast(
        cls,
        latitude: float,
        longitude: float,
        hours: int = 24,
    ) -> dict[str, Any]:
        """
        Retrieve an hourly weather forecast for the provided coordinates.

        Args:
            latitude:
                Latitude between -90 and 90.

            longitude:
                Longitude between -180 and 180.

            hours:
                Number of forecast hours between 1 and 168.

        Returns:
            A normalized dictionary containing location information,
            hourly forecasts, and measurement units.

        Raises:
            HourlyForecastServiceUnavailableError:
                When Open-Meteo cannot be reached.

            HourlyForecastServiceError:
                When Open-Meteo returns invalid or incomplete data.
        """

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(cls.HOURLY_VARIABLES),

            # Return hourly data starting from the current hour.
            "forecast_hours": hours,

            # Resolve local timestamps from the coordinates.
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
            raise HourlyForecastServiceUnavailableError(
                "The hourly forecast service did not respond in time."
            ) from exc

        except requests.ConnectionError as exc:
            raise HourlyForecastServiceUnavailableError(
                "The hourly forecast service is currently unavailable."
            ) from exc

        except requests.HTTPError as exc:
            raise HourlyForecastServiceError(
                "The hourly forecast service returned an HTTP error."
            ) from exc

        except requests.RequestException as exc:
            raise HourlyForecastServiceError(
                "An unexpected error occurred while contacting "
                "the hourly forecast service."
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise HourlyForecastServiceError(
                "The hourly forecast service returned invalid JSON."
            ) from exc

        hourly = payload.get("hourly")
        hourly_units = payload.get("hourly_units")

        if not isinstance(hourly, dict):
            raise HourlyForecastServiceError(
                "The hourly forecast service returned invalid hourly data."
            )

        if not isinstance(hourly_units, dict):
            hourly_units = {}

        return cls._normalize_response(
            payload=payload,
            hourly=hourly,
            hourly_units=hourly_units,
        )

    @classmethod
    def _normalize_response(
        cls,
        payload: dict[str, Any],
        hourly: dict[str, Any],
        hourly_units: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Convert Open-Meteo parallel hourly arrays into
        one normalized object per forecast hour.
        """

        timestamps = hourly.get("time")

        if not isinstance(timestamps, list):
            raise HourlyForecastServiceError(
                "The hourly forecast service returned invalid timestamps."
            )

        forecasts = []

        for index, timestamp in enumerate(timestamps):
            is_day_value = cls._get_value(
                hourly,
                "is_day",
                index,
            )

            forecasts.append(
                {
                    "time": timestamp,
                    "temperature": cls._get_value(
                        hourly,
                        "temperature_2m",
                        index,
                    ),
                    "relative_humidity": cls._get_value(
                        hourly,
                        "relative_humidity_2m",
                        index,
                    ),
                    "apparent_temperature": cls._get_value(
                        hourly,
                        "apparent_temperature",
                        index,
                    ),
                    "precipitation_probability": cls._get_value(
                        hourly,
                        "precipitation_probability",
                        index,
                    ),
                    "precipitation": cls._get_value(
                        hourly,
                        "precipitation",
                        index,
                    ),
                    "rain": cls._get_value(
                        hourly,
                        "rain",
                        index,
                    ),
                    "showers": cls._get_value(
                        hourly,
                        "showers",
                        index,
                    ),
                    "snowfall": cls._get_value(
                        hourly,
                        "snowfall",
                        index,
                    ),
                    "weather_code": cls._get_value(
                        hourly,
                        "weather_code",
                        index,
                    ),
                    "cloud_cover": cls._get_value(
                        hourly,
                        "cloud_cover",
                        index,
                    ),
                    "visibility": cls._get_value(
                        hourly,
                        "visibility",
                        index,
                    ),
                    "wind_speed": cls._get_value(
                        hourly,
                        "wind_speed_10m",
                        index,
                    ),
                    "wind_direction": cls._get_value(
                        hourly,
                        "wind_direction_10m",
                        index,
                    ),
                    "wind_gusts": cls._get_value(
                        hourly,
                        "wind_gusts_10m",
                        index,
                    ),
                    "is_day": (
                        bool(is_day_value)
                        if is_day_value is not None
                        else None
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
                "utc_offset_seconds": payload.get(
                    "utc_offset_seconds"
                ),
            },
            "hourly": forecasts,
            "units": {
                "temperature": hourly_units.get("temperature_2m"),
                "relative_humidity": hourly_units.get(
                    "relative_humidity_2m"
                ),
                "apparent_temperature": hourly_units.get(
                    "apparent_temperature"
                ),
                "precipitation_probability": hourly_units.get(
                    "precipitation_probability"
                ),
                "precipitation": hourly_units.get("precipitation"),
                "rain": hourly_units.get("rain"),
                "showers": hourly_units.get("showers"),
                "snowfall": hourly_units.get("snowfall"),
                "weather_code": hourly_units.get("weather_code"),
                "cloud_cover": hourly_units.get("cloud_cover"),
                "visibility": hourly_units.get("visibility"),
                "wind_speed": hourly_units.get("wind_speed_10m"),
                "wind_direction": hourly_units.get(
                    "wind_direction_10m"
                ),
                "wind_gusts": hourly_units.get("wind_gusts_10m"),
            },
        }

    @staticmethod
    def _get_value(
        data: dict[str, Any],
        key: str,
        index: int,
    ) -> Any:
        """
        Safely retrieve a value from an Open-Meteo hourly data array.
        """

        values = data.get(key)

        if not isinstance(values, list):
            return None

        if index >= len(values):
            return None

        return values[index]