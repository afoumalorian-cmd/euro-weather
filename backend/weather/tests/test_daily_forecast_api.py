from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from weather.services.daily_forecast_service import (
    DailyForecastServiceError,
    DailyForecastServiceUnavailableError,
)
from weather.services.geocoding_service import (
    GeocodingServiceError,
    GeocodingServiceUnavailableError,
)


class DailyForecastApiTests(APITestCase):
    """
    Test daily forecast endpoints using coordinates and city names.
    """

    def setUp(self):
        """
        Resolve endpoint URLs and prepare normalized mock data.
        """

        self.coordinate_url = reverse(
            "weather:daily-forecast"
        )
        self.city_url = reverse(
            "weather:daily-forecast-by-city"
        )

        self.location = {
            "id": 2988507,
            "name": "Paris",
            "latitude": 48.85341,
            "longitude": 2.3488,
            "elevation": 42,
            "timezone": "Europe/Paris",
            "country": "France",
            "country_code": "FR",
        }

        self.forecast_response = {
            "location": {
                "latitude": 48.85341,
                "longitude": 2.3488,
                "elevation": 42,
                "timezone": "Europe/Paris",
                "timezone_abbreviation": "CEST",
                "utc_offset_seconds": 7200,
            },
            "daily": [
                {
                    "date": "2026-08-01",
                    "weather_code": 1,
                    "temperature_max": 25.4,
                    "temperature_min": 16.2,
                    "apparent_temperature_max": 26.1,
                    "apparent_temperature_min": 15.8,
                    "sunrise": "2026-08-01T06:24",
                    "sunset": "2026-08-01T21:28",
                    "precipitation_sum": 0,
                    "rain_sum": 0,
                    "showers_sum": 0,
                    "snowfall_sum": 0,
                    "precipitation_hours": 0,
                    "precipitation_probability_max": 10,
                    "wind_speed_max": 14.5,
                    "wind_gusts_max": 26.2,
                    "wind_direction_dominant": 220,
                },
            ],
            "units": {
                "temperature_max": "°C",
                "temperature_min": "°C",
                "precipitation_sum": "mm",
                "wind_speed_max": "km/h",
            },
        }

    @patch(
        "weather.views."
        "DailyForecastService.get_daily_forecast"
    )
    def test_returns_daily_forecast_for_valid_coordinates(
        self,
        mocked_service,
    ):
        """
        Valid coordinates return normalized daily forecast data.
        """

        mocked_service.return_value = self.forecast_response

        response = self.client.get(
            self.coordinate_url,
            {
                "latitude": 48.8566,
                "longitude": 2.3522,
                "days": 7,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertTrue(
            response.data["success"]
        )
        self.assertEqual(
            response.data["data"],
            self.forecast_response,
        )

        mocked_service.assert_called_once_with(
            latitude=48.8566,
            longitude=2.3522,
            days=7,
        )

    @patch(
        "weather.views."
        "DailyForecastService.get_daily_forecast"
    )
    def test_uses_seven_days_by_default(
        self,
        mocked_service,
    ):
        """
        The coordinate endpoint uses seven forecast days by default.
        """

        mocked_service.return_value = self.forecast_response

        response = self.client.get(
            self.coordinate_url,
            {
                "latitude": 48.8566,
                "longitude": 2.3522,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        mocked_service.assert_called_once_with(
            latitude=48.8566,
            longitude=2.3522,
            days=7,
        )

    def test_returns_400_when_coordinates_are_missing(self):
        """
        Latitude and longitude are required.
        """

        response = self.client.get(
            self.coordinate_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "latitude",
            response.data["errors"],
        )
        self.assertIn(
            "longitude",
            response.data["errors"],
        )

    def test_returns_400_for_invalid_number_of_days(self):
        """
        Forecast duration must remain between 1 and 16 days.
        """

        response = self.client.get(
            self.coordinate_url,
            {
                "latitude": 48.8566,
                "longitude": 2.3522,
                "days": 17,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "days",
            response.data["errors"],
        )

    @patch(
        "weather.views."
        "DailyForecastService.get_daily_forecast"
    )
    def test_returns_503_when_forecast_service_is_unavailable(
        self,
        mocked_service,
    ):
        """
        An unavailable forecast provider returns HTTP 503.
        """

        mocked_service.side_effect = (
            DailyForecastServiceUnavailableError(
                "The forecast service is currently unavailable."
            )
        )

        response = self.client.get(
            self.coordinate_url,
            {
                "latitude": 48.8566,
                "longitude": 2.3522,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        self.assertEqual(
            response.data["error"],
            "The forecast service is currently unavailable.",
        )

    @patch(
        "weather.views."
        "DailyForecastService.get_daily_forecast"
    )
    def test_returns_502_for_invalid_forecast_response(
        self,
        mocked_service,
    ):
        """
        Invalid provider data returns HTTP 502.
        """

        mocked_service.side_effect = (
            DailyForecastServiceError(
                "The forecast service returned invalid daily data."
            )
        )

        response = self.client.get(
            self.coordinate_url,
            {
                "latitude": 48.8566,
                "longitude": 2.3522,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_502_BAD_GATEWAY,
        )
        self.assertEqual(
            response.data["error"],
            "The forecast service returned invalid daily data.",
        )

    @patch(
        "weather.views."
        "DailyForecastService.get_daily_forecast"
    )
    @patch(
        "weather.views."
        "GeocodingService.find_location_by_country_name"
    )
    def test_returns_daily_forecast_by_city(
        self,
        mocked_geocoding,
        mocked_forecast,
    ):
        """
        A valid city and country are resolved before loading forecasts.
        """

        mocked_geocoding.return_value = self.location
        mocked_forecast.return_value = self.forecast_response

        response = self.client.get(
            self.city_url,
            {
                "city": "Paris",
                "country": "France",
                "days": 7,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertTrue(
            response.data["success"]
        )
        self.assertEqual(
            response.data["location"],
            self.location,
        )
        self.assertEqual(
            response.data["data"],
            self.forecast_response,
        )

        mocked_geocoding.assert_called_once_with(
            city="Paris",
            country="France",
        )
        mocked_forecast.assert_called_once_with(
            latitude=48.85341,
            longitude=2.3488,
            days=7,
        )

    def test_returns_400_when_city_or_country_is_missing(self):
        """
        City and country are required by the city endpoint.
        """

        response = self.client.get(
            self.city_url,
            {
                "city": "Paris",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "country",
            response.data["errors"],
        )

    @patch(
        "weather.views."
        "GeocodingService.find_location_by_country_name"
    )
    def test_returns_404_when_city_is_not_found(
        self,
        mocked_geocoding,
    ):
        """
        An unknown city and country combination returns HTTP 404.
        """

        mocked_geocoding.return_value = None

        response = self.client.get(
            self.city_url,
            {
                "city": "Unknown City",
                "country": "France",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertFalse(
            response.data["success"]
        )

    @patch(
        "weather.views."
        "GeocodingService.find_location_by_country_name"
    )
    def test_returns_503_when_geocoding_is_unavailable(
        self,
        mocked_geocoding,
    ):
        """
        An unavailable geocoding provider returns HTTP 503.
        """

        mocked_geocoding.side_effect = (
            GeocodingServiceUnavailableError(
                "The geocoding service is unavailable."
            )
        )

        response = self.client.get(
            self.city_url,
            {
                "city": "Paris",
                "country": "France",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        self.assertEqual(
            response.data["error"],
            "The geocoding service is unavailable.",
        )

    @patch(
        "weather.views."
        "GeocodingService.find_location_by_country_name"
    )
    def test_returns_502_for_invalid_geocoding_response(
        self,
        mocked_geocoding,
    ):
        """
        Invalid geocoding data returns HTTP 502.
        """

        mocked_geocoding.side_effect = (
            GeocodingServiceError(
                "The geocoding service returned invalid data."
            )
        )

        response = self.client.get(
            self.city_url,
            {
                "city": "Paris",
                "country": "France",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_502_BAD_GATEWAY,
        )
        self.assertEqual(
            response.data["error"],
            "The geocoding service returned invalid data.",
        )

    @patch(
        "weather.views."
        "DailyForecastService.get_daily_forecast"
    )
    @patch(
        "weather.views."
        "GeocodingService.find_location_by_country_name"
    )
    def test_returns_503_when_city_forecast_service_is_unavailable(
        self,
        mocked_geocoding,
        mocked_forecast,
    ):
        """
        Forecast provider failures also return 503 on the city endpoint.
        """

        mocked_geocoding.return_value = self.location
        mocked_forecast.side_effect = (
            DailyForecastServiceUnavailableError(
                "The forecast service is currently unavailable."
            )
        )

        response = self.client.get(
            self.city_url,
            {
                "city": "Paris",
                "country": "France",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )