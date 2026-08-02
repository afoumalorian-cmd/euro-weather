from unittest.mock import Mock, patch

from django.core.cache import cache
from django.test import SimpleTestCase

from weather.services.hourly_forecast_service import HourlyForecastService


class HourlyForecastServiceCacheTests(SimpleTestCase):
    """
    Test the cache behavior of the hourly forecast service.
    """

    def setUp(self) -> None:
        """
        Clear the cache before each test.
        """
        cache.clear()

    @patch(
        "weather.services.hourly_forecast_service.requests.get"
    )
    def test_identical_requests_use_cached_response(
        self,
        mock_get: Mock,
    ) -> None:
        """
        Ensure identical hourly requests call Open-Meteo only once.
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
            "hourly": {
                "time": ["2026-08-03T00:00"],
                "temperature_2m": [19.0],
                "relative_humidity_2m": [72],
                "apparent_temperature": [19.5],
                "precipitation_probability": [10],
                "precipitation": [0.0],
                "rain": [0.0],
                "showers": [0.0],
                "snowfall": [0.0],
                "weather_code": [1],
                "cloud_cover": [20],
                "visibility": [24000.0],
                "wind_speed_10m": [9.0],
                "wind_direction_10m": [220],
                "wind_gusts_10m": [17.0],
                "is_day": [0],
            },
            "hourly_units": {
                "temperature_2m": "°C",
                "relative_humidity_2m": "%",
                "apparent_temperature": "°C",
                "precipitation_probability": "%",
                "precipitation": "mm",
                "rain": "mm",
                "showers": "mm",
                "snowfall": "cm",
                "weather_code": "wmo code",
                "cloud_cover": "%",
                "visibility": "m",
                "wind_speed_10m": "km/h",
                "wind_direction_10m": "°",
                "wind_gusts_10m": "km/h",
            },
        }
        mock_get.return_value = mock_response

        first_result = HourlyForecastService.get_hourly_forecast(
            latitude=48.8566,
            longitude=2.3522,
            forecast_date="2026-08-03",
        )

        second_result = HourlyForecastService.get_hourly_forecast(
            latitude=48.8566,
            longitude=2.3522,
            forecast_date="2026-08-03",
        )

        self.assertEqual(first_result, second_result)
        self.assertEqual(mock_get.call_count, 1)

    @patch(
        "weather.services.hourly_forecast_service.requests.get"
    )
    def test_different_dates_create_different_cache_entries(
        self,
        mock_get: Mock,
    ) -> None:
        """
        Ensure different dates do not share the same cache entry.
        """
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "latitude": 48.8566,
            "longitude": 2.3522,
            "hourly": {
                "time": [],
            },
            "hourly_units": {},
        }
        mock_get.return_value = mock_response

        HourlyForecastService.get_hourly_forecast(
            latitude=48.8566,
            longitude=2.3522,
            forecast_date="2026-08-03",
        )

        HourlyForecastService.get_hourly_forecast(
            latitude=48.8566,
            longitude=2.3522,
            forecast_date="2026-08-04",
        )

        self.assertEqual(mock_get.call_count, 2)