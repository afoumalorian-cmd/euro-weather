from unittest.mock import Mock, patch

from django.core.cache import cache
from django.test import SimpleTestCase

from weather.services.historical_weather_service import (
    HistoricalWeatherService,
)


class HistoricalWeatherServiceCacheTests(SimpleTestCase):
    """
    Test the cache behavior of the historical weather service.
    """

    def setUp(self) -> None:
        """
        Clear the cache before each test.
        """
        cache.clear()

    @patch(
        "weather.services.historical_weather_service.requests.get"
    )
    def test_identical_requests_use_cached_response(
        self,
        mock_get: Mock,
    ) -> None:
        """
        Ensure identical historical requests call Open-Meteo only once.
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
            "daily": {
                "time": ["2026-07-01"],
                "weather_code": [1],
                "temperature_2m_max": [26.0],
                "temperature_2m_min": [17.0],
                "temperature_2m_mean": [21.5],
                "apparent_temperature_max": [27.0],
                "apparent_temperature_min": [16.5],
                "precipitation_sum": [0.0],
                "rain_sum": [0.0],
                "snowfall_sum": [0.0],
                "precipitation_hours": [0.0],
                "wind_speed_10m_max": [11.0],
                "wind_gusts_10m_max": [20.0],
                "wind_direction_10m_dominant": [230],
                "sunrise": ["2026-07-01T05:50"],
                "sunset": ["2026-07-01T21:58"],
            },
            "daily_units": {
                "weather_code": "wmo code",
                "temperature_2m_max": "°C",
                "temperature_2m_min": "°C",
                "temperature_2m_mean": "°C",
                "apparent_temperature_max": "°C",
                "apparent_temperature_min": "°C",
                "precipitation_sum": "mm",
                "rain_sum": "mm",
                "snowfall_sum": "cm",
                "precipitation_hours": "h",
                "wind_speed_10m_max": "km/h",
                "wind_gusts_10m_max": "km/h",
                "wind_direction_10m_dominant": "°",
                "sunrise": "iso8601",
                "sunset": "iso8601",
            },
        }
        mock_get.return_value = mock_response

        first_result = HistoricalWeatherService.get_historical_weather(
            latitude=48.8566,
            longitude=2.3522,
            start_date="2026-07-01",
            end_date="2026-07-01",
        )

        second_result = HistoricalWeatherService.get_historical_weather(
            latitude=48.8566,
            longitude=2.3522,
            start_date="2026-07-01",
            end_date="2026-07-01",
        )

        self.assertEqual(first_result, second_result)
        self.assertEqual(mock_get.call_count, 1)

    @patch(
        "weather.services.historical_weather_service.requests.get"
    )
    def test_different_date_ranges_create_different_cache_entries(
        self,
        mock_get: Mock,
    ) -> None:
        """
        Ensure different date ranges do not share a cache entry.
        """
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "latitude": 48.8566,
            "longitude": 2.3522,
            "daily": {
                "time": [],
            },
            "daily_units": {},
        }
        mock_get.return_value = mock_response

        HistoricalWeatherService.get_historical_weather(
            latitude=48.8566,
            longitude=2.3522,
            start_date="2026-07-01",
            end_date="2026-07-07",
        )

        HistoricalWeatherService.get_historical_weather(
            latitude=48.8566,
            longitude=2.3522,
            start_date="2026-07-01",
            end_date="2026-07-08",
        )

        self.assertEqual(mock_get.call_count, 2)