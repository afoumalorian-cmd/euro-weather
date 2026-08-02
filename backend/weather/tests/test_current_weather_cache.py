from unittest.mock import Mock, patch

from django.core.cache import cache
from django.test import SimpleTestCase

from weather.services.current_weather_service import CurrentWeatherService


class CurrentWeatherServiceCacheTests(SimpleTestCase):
    """
    Test the cache behavior of the current weather service.
    """

    def setUp(self) -> None:
        """
        Clear the cache before each test.
        """
        cache.clear()

    @patch(
        "weather.services.current_weather_service.requests.get"
    )
    def test_identical_requests_use_cached_response(
        self,
        mock_get: Mock,
    ) -> None:
        """
        Ensure identical weather requests call Open-Meteo only once.
        """
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "latitude": 48.8566,
            "longitude": 2.3522,
            "elevation": 35.0,
            "timezone": "Europe/Paris",
            "timezone_abbreviation": "GMT+2",
            "utc_offset_seconds": 7200,
            "current": {
                "time": "2026-08-03T00:00",
                "interval": 900,
                "temperature_2m": 20.0,
                "relative_humidity_2m": 70,
                "apparent_temperature": 20.5,
                "precipitation": 0.0,
                "weather_code": 1,
                "cloud_cover": 25,
                "wind_speed_10m": 10.0,
                "wind_direction_10m": 220,
                "wind_gusts_10m": 18.0,
                "is_day": 0,
            },
            "current_units": {
                "temperature_2m": "°C",
                "relative_humidity_2m": "%",
                "apparent_temperature": "°C",
                "precipitation": "mm",
                "weather_code": "wmo code",
                "cloud_cover": "%",
                "wind_speed_10m": "km/h",
                "wind_direction_10m": "°",
                "wind_gusts_10m": "km/h",
            },
        }
        mock_get.return_value = mock_response

        first_result = CurrentWeatherService.get_current_weather(
            latitude=48.8566,
            longitude=2.3522,
        )

        second_result = CurrentWeatherService.get_current_weather(
            latitude=48.8566,
            longitude=2.3522,
        )

        self.assertEqual(first_result, second_result)
        self.assertEqual(mock_get.call_count, 1)

    @patch(
        "weather.services.current_weather_service.requests.get"
    )
    def test_different_coordinates_create_different_cache_entries(
        self,
        mock_get: Mock,
    ) -> None:
        """
        Ensure different coordinates do not share a cache entry.
        """
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "latitude": 48.8566,
            "longitude": 2.3522,
            "current": {},
            "current_units": {},
        }
        mock_get.return_value = mock_response

        CurrentWeatherService.get_current_weather(
            latitude=48.8566,
            longitude=2.3522,
        )

        CurrentWeatherService.get_current_weather(
            latitude=45.7640,
            longitude=4.8357,
        )

        self.assertEqual(mock_get.call_count, 2)