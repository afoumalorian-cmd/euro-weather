from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from weather.services.current_weather_service import (
    CurrentWeatherServiceError,
    CurrentWeatherServiceUnavailableError,
)


class CurrentWeatherApiTests(APITestCase):
    """
    Test the current weather API endpoint.
    """

    def setUp(self):
        """
        Resolve the current weather endpoint URL.
        """

        self.url = reverse(
            "weather:current-weather"
        )

        self.valid_parameters = {
            "latitude": 48.8566,
            "longitude": 2.3522,
        }

        self.service_response = {
            "location": {
                "latitude": 48.8566,
                "longitude": 2.3522,
                "elevation": 35,
                "timezone": "Europe/Paris",
                "timezone_abbreviation": "CEST",
                "utc_offset_seconds": 7200,
            },
            "current": {
                "time": "2026-08-01T15:00",
                "interval": 900,
                "temperature": 23.5,
                "relative_humidity": 55,
                "apparent_temperature": 24.1,
                "precipitation": 0,
                "weather_code": 1,
                "cloud_cover": 20,
                "wind_speed": 12.4,
                "wind_direction": 210,
                "wind_gusts": 18.7,
                "is_day": True,
            },
            "units": {
                "temperature": "°C",
                "relative_humidity": "%",
                "apparent_temperature": "°C",
                "precipitation": "mm",
                "weather_code": "wmo code",
                "cloud_cover": "%",
                "wind_speed": "km/h",
                "wind_direction": "°",
                "wind_gusts": "km/h",
            },
        }

    @patch(
        "weather.views."
        "CurrentWeatherService.get_current_weather"
    )
    def test_returns_current_weather_for_valid_coordinates(
        self,
        mocked_service,
    ):
        """
        Valid coordinates return normalized current weather data.
        """

        mocked_service.return_value = self.service_response

        response = self.client.get(
            self.url,
            self.valid_parameters,
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
            self.service_response,
        )

        mocked_service.assert_called_once_with(
            latitude=48.8566,
            longitude=2.3522,
        )

    @patch(
        "weather.views."
        "CurrentWeatherService.get_current_weather"
    )
    def test_accepts_boundary_coordinate_values(
        self,
        mocked_service,
    ):
        """
        Latitude and longitude boundary values are accepted.
        """

        mocked_service.return_value = self.service_response

        response = self.client.get(
            self.url,
            {
                "latitude": -90,
                "longitude": 180,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        mocked_service.assert_called_once_with(
            latitude=-90.0,
            longitude=180.0,
        )

    def test_returns_400_when_latitude_is_missing(self):
        """
        Latitude is required.
        """

        response = self.client.get(
            self.url,
            {
                "longitude": 2.3522,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            response.data["success"]
        )

        self.assertIn(
            "latitude",
            response.data["errors"],
        )

    def test_returns_400_when_longitude_is_missing(self):
        """
        Longitude is required.
        """

        response = self.client.get(
            self.url,
            {
                "latitude": 48.8566,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "longitude",
            response.data["errors"],
        )

    def test_returns_400_for_invalid_latitude(self):
        """
        Latitude must remain between -90 and 90.
        """

        response = self.client.get(
            self.url,
            {
                "latitude": 91,
                "longitude": 2.3522,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "latitude",
            response.data["errors"],
        )

    def test_returns_400_for_invalid_longitude(self):
        """
        Longitude must remain between -180 and 180.
        """

        response = self.client.get(
            self.url,
            {
                "latitude": 48.8566,
                "longitude": 181,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "longitude",
            response.data["errors"],
        )

    def test_returns_400_for_non_numeric_coordinates(self):
        """
        Coordinates must contain valid numbers.
        """

        response = self.client.get(
            self.url,
            {
                "latitude": "Paris",
                "longitude": "France",
            },
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

    @patch(
        "weather.views."
        "CurrentWeatherService.get_current_weather"
    )
    def test_returns_503_when_weather_service_is_unavailable(
        self,
        mocked_service,
    ):
        """
        Service connection problems return HTTP 503.
        """

        mocked_service.side_effect = (
            CurrentWeatherServiceUnavailableError(
                "The weather service is currently unavailable."
            )
        )

        response = self.client.get(
            self.url,
            self.valid_parameters,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )

        self.assertFalse(
            response.data["success"]
        )

        self.assertEqual(
            response.data["error"],
            "The weather service is currently unavailable.",
        )

    @patch(
        "weather.views."
        "CurrentWeatherService.get_current_weather"
    )
    def test_returns_502_for_invalid_weather_service_response(
        self,
        mocked_service,
    ):
        """
        Invalid external service data returns HTTP 502.
        """

        mocked_service.side_effect = (
            CurrentWeatherServiceError(
                "The weather service returned invalid current weather data."
            )
        )

        response = self.client.get(
            self.url,
            self.valid_parameters,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_502_BAD_GATEWAY,
        )

        self.assertFalse(
            response.data["success"]
        )

        self.assertEqual(
            response.data["error"],
            (
                "The weather service returned invalid "
                "current weather data."
            ),
        )