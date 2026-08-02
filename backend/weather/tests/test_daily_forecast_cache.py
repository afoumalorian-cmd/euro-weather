from unittest.mock import Mock, patch

from django.core.cache import cache
from django.test import SimpleTestCase

from weather.services.daily_forecast_service import DailyForecastService


class DailyForecastServiceCacheTests(SimpleTestCase):
    """
    Test the cache behavior of the daily forecast service.
    """

    def setUp(self) -> None:
        """
        Clear the cache before each test.
        """
        cache.clear()

    @patch(
        "weather.services.daily_forecast_service.requests.get"
    )
    def test_identical_requests_use_cached_response(
        self,
        mock_get: Mock,
    ) -> None:
        """
        Ensure identical forecasts are fetched from Open-Meteo only once.
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
                "time": ["2026-08-03"],
                "weather_code": [1],
                "temperature_2m_max": [25.0],
                "temperature_2m_min": [16.0],
                "apparent_temperature_max": [25.5],
                "apparent_temperature_min": [15.5],
                "sunrise": ["2026-08-03T06:25"],
                "sunset": ["2026-08-03T21:25"],
                "precipitation_sum": [0.0],
                "rain_sum": [0.0],
                "showers_sum": [0.0],
                "snowfall_sum": [0.0],
                "precipitation_hours": [0.0],
                "precipitation_probability_max": [10],
                "wind_speed_10m_max": [12.0],
                "wind_gusts_10m_max": [22.0],
                "wind_direction_10m_dominant": [240],
            },
            "daily_units": {
                "weather_code": "wmo code",
                "temperature_2m_max": "°C",
                "temperature_2m_min": "°C",
                "apparent_temperature_max": "°C",
                "apparent_temperature_min": "°C",
                "sunrise": "iso8601",
                "sunset": "iso8601",
                "precipitation_sum": "mm",
                "rain_sum": "mm",
                "showers_sum": "mm",
                "snowfall_sum": "cm",
                "precipitation_hours": "h",
                "precipitation_probability_max": "%",
                "wind_speed_10m_max": "km/h",
                "wind_gusts_10m_max": "km/h",
                "wind_direction_10m_dominant": "°",
            },
        }
        mock_get.return_value = mock_response

        first_result = DailyForecastService.get_daily_forecast(
            latitude=48.8566,
            longitude=2.3522,
            days=7,
        )

        second_result = DailyForecastService.get_daily_forecast(
            latitude=48.8566,
            longitude=2.3522,
            days=7,
        )

        self.assertEqual(first_result, second_result)
        self.assertEqual(mock_get.call_count, 1)

    @patch(
        "weather.services.daily_forecast_service.requests.get"
    )
    def test_different_parameters_create_different_cache_entries(
        self,
        mock_get: Mock,
    ) -> None:
        """
        Ensure different forecast parameters do not share a cache entry.
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

        DailyForecastService.get_daily_forecast(
            latitude=48.8566,
            longitude=2.3522,
            days=7,
        )

        DailyForecastService.get_daily_forecast(
            latitude=48.8566,
            longitude=2.3522,
            days=5,
        )

        self.assertEqual(mock_get.call_count, 2)