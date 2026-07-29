from typing import Any

import requests


class HistoricalWeatherServiceError(Exception):
    """
    Base exception raised when the historical weather service
    cannot return valid data.
    """


class HistoricalWeatherServiceUnavailableError(
    HistoricalWeatherServiceError
):
    """
    Exception raised when the Open-Meteo Historical Weather API
    is unavailable or does not respond before the timeout.
    """


class HistoricalWeatherService:
    """
    Retrieve and normalize historical daily weather data
    from the Open-Meteo Historical Weather API.
    """

    BASE_URL = "https://archive-api.open-meteo.com/v1/archive"
    REQUEST_TIMEOUT = 10

    DAILY_VARIABLES = [
        "weather_code",
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",
        "apparent_temperature_max",
        "apparent_temperature_min",
        "precipitation_sum",
        "rain_sum",
        "snowfall_sum",
        "precipitation_hours",
        "wind_speed_10m_max",
        "wind_gusts_10m_max",
        "wind_direction_10m_dominant",
        "sunrise",
        "sunset",
    ]

    @classmethod
    def get_historical_weather(
        cls,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
    ) -> dict[str, Any]:
        """
        Retrieve historical daily weather data for a date range.

        Args:
            latitude:
                Latitude between -90 and 90.

            longitude:
                Longitude between -180 and 180.

            start_date:
                First historical date in YYYY-MM-DD format.

            end_date:
                Last historical date in YYYY-MM-DD format.

        Returns:
            A normalized dictionary containing location information,
            historical daily records, and measurement units.

        Raises:
            HistoricalWeatherServiceUnavailableError:
                When Open-Meteo cannot be reached.

            HistoricalWeatherServiceError:
                When Open-Meteo returns invalid or incomplete data.
        """

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ",".join(cls.DAILY_VARIABLES),

            # Daily timestamps must use the location's local timezone.
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
            raise HistoricalWeatherServiceUnavailableError(
                "The historical weather service did not respond in time."
            ) from exc

        except requests.ConnectionError as exc:
            raise HistoricalWeatherServiceUnavailableError(
                "The historical weather service is currently unavailable."
            ) from exc

        except requests.HTTPError as exc:
            raise HistoricalWeatherServiceError(
                "The historical weather service returned an HTTP error."
            ) from exc

        except requests.RequestException as exc:
            raise HistoricalWeatherServiceError(
                "An unexpected error occurred while contacting "
                "the historical weather service."
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise HistoricalWeatherServiceError(
                "The historical weather service returned invalid JSON."
            ) from exc

        daily = payload.get("daily")
        daily_units = payload.get("daily_units")

        if not isinstance(daily, dict):
            raise HistoricalWeatherServiceError(
                "The historical weather service returned invalid daily data."
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
        Convert Open-Meteo parallel daily arrays into
        one normalized object per historical day.
        """

        dates = daily.get("time")

        if not isinstance(dates, list):
            raise HistoricalWeatherServiceError(
                "The historical weather service returned invalid dates."
            )

        records = []

        for index, historical_date in enumerate(dates):
            records.append(
                {
                    "date": historical_date,
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
                    "temperature_mean": cls._get_value(
                        daily,
                        "temperature_2m_mean",
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
            "daily": records,
            "units": {
                "weather_code": daily_units.get("weather_code"),
                "temperature_max": daily_units.get(
                    "temperature_2m_max"
                ),
                "temperature_min": daily_units.get(
                    "temperature_2m_min"
                ),
                "temperature_mean": daily_units.get(
                    "temperature_2m_mean"
                ),
                "apparent_temperature_max": daily_units.get(
                    "apparent_temperature_max"
                ),
                "apparent_temperature_min": daily_units.get(
                    "apparent_temperature_min"
                ),
                "precipitation_sum": daily_units.get(
                    "precipitation_sum"
                ),
                "rain_sum": daily_units.get("rain_sum"),
                "snowfall_sum": daily_units.get("snowfall_sum"),
                "precipitation_hours": daily_units.get(
                    "precipitation_hours"
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
                "sunrise": daily_units.get("sunrise"),
                "sunset": daily_units.get("sunset"),
            },
        }

    @staticmethod
    def _get_value(
        data: dict[str, Any],
        key: str,
        index: int,
    ) -> Any:
        """
        Safely retrieve a value from an Open-Meteo daily data array.
        """

        values = data.get(key)

        if not isinstance(values, list):
            return None

        if index >= len(values):
            return None

        return values[index]