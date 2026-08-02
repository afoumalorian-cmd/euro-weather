from typing import Any

import requests
from django.core.cache import cache

from weather.cache_utils import (
    CURRENT_WEATHER_CACHE_TIMEOUT,
    build_cache_key,
)

class CurrentWeatherServiceError(Exception):
    """
    Exception générique levée lorsqu'une erreur survient
    pendant l'appel à l'API météo Open-Meteo.
    """


class CurrentWeatherServiceUnavailableError(CurrentWeatherServiceError):
    """
    Exception levée lorsque l'API Open-Meteo est inaccessible
    ou ne répond pas dans le délai prévu.
    """


class CurrentWeatherService:
    """
    Service responsable de la récupération des conditions
    météorologiques actuelles depuis Open-Meteo.
    """

    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    REQUEST_TIMEOUT = 10

    CURRENT_VARIABLES = [
        "temperature_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "precipitation",
        "weather_code",
        "cloud_cover",
        "wind_speed_10m",
        "wind_direction_10m",
        "wind_gusts_10m",
        "is_day",
    ]

    @classmethod
    def get_current_weather(
        cls,
        latitude: float,
        longitude: float,
    ) -> dict[str, Any]:
        """
        Récupère les conditions météorologiques actuelles
        pour les coordonnées fournies.

        Args:
            latitude:
                Latitude comprise entre -90 et 90.

            longitude:
                Longitude comprise entre -180 et 180.

        Returns:
            Une réponse météo normalisée.

        Raises:
            CurrentWeatherServiceUnavailableError:
                Lorsque l'API Open-Meteo est inaccessible.

            CurrentWeatherServiceError:
                Lorsque la réponse reçue est invalide.
        """
        cache_key = build_cache_key(
            "current_weather",
            latitude=latitude,
            longitude=longitude,
        )

        cached_weather = cache.get(cache_key)

        if cached_weather is not None:
            return cached_weather
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join(cls.CURRENT_VARIABLES),

            # Demande à Open-Meteo de déterminer automatiquement
            # le fuseau horaire correspondant aux coordonnées.
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
            raise CurrentWeatherServiceUnavailableError(
                "The weather service did not respond in time."
            ) from exc

        except requests.ConnectionError as exc:
            raise CurrentWeatherServiceUnavailableError(
                "The weather service is currently unavailable."
            ) from exc

        except requests.HTTPError as exc:
            raise CurrentWeatherServiceError(
                "The weather service returned an HTTP error."
            ) from exc

        except requests.RequestException as exc:
            raise CurrentWeatherServiceError(
                "An unexpected error occurred while contacting "
                "the weather service."
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise CurrentWeatherServiceError(
                "The weather service returned an invalid JSON response."
            ) from exc

        current = payload.get("current")
        current_units = payload.get("current_units")

        if not isinstance(current, dict):
            raise CurrentWeatherServiceError(
                "The weather service returned invalid current weather data."
            )

        if not isinstance(current_units, dict):
            current_units = {}

        normalized_weather = cls._normalize_response(
            payload=payload,
            current=current,
            current_units=current_units,
        )

        cache.set(
            cache_key,
            normalized_weather,
            timeout=CURRENT_WEATHER_CACHE_TIMEOUT,
        )

        return normalized_weather

    @staticmethod
    def _normalize_response(
        payload: dict[str, Any],
        current: dict[str, Any],
        current_units: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Transforme la réponse Open-Meteo en une structure
        stable contrôlée par notre API.
        """

        is_day_value = current.get("is_day")

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
            "current": {
                "time": current.get("time"),
                "interval": current.get("interval"),
                "temperature": current.get("temperature_2m"),
                "relative_humidity": current.get(
                    "relative_humidity_2m"
                ),
                "apparent_temperature": current.get(
                    "apparent_temperature"
                ),
                "precipitation": current.get("precipitation"),
                "weather_code": current.get("weather_code"),
                "cloud_cover": current.get("cloud_cover"),
                "wind_speed": current.get("wind_speed_10m"),
                "wind_direction": current.get(
                    "wind_direction_10m"
                ),
                "wind_gusts": current.get("wind_gusts_10m"),
                "is_day": (
                    bool(is_day_value)
                    if is_day_value is not None
                    else None
                ),
            },
            "units": {
                "temperature": current_units.get("temperature_2m"),
                "relative_humidity": current_units.get(
                    "relative_humidity_2m"
                ),
                "apparent_temperature": current_units.get(
                    "apparent_temperature"
                ),
                "precipitation": current_units.get("precipitation"),
                "weather_code": current_units.get("weather_code"),
                "cloud_cover": current_units.get("cloud_cover"),
                "wind_speed": current_units.get("wind_speed_10m"),
                "wind_direction": current_units.get(
                    "wind_direction_10m"
                ),
                "wind_gusts": current_units.get("wind_gusts_10m"),
            },
        }