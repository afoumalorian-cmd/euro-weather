from datetime import date, timedelta
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from weather.services.geocoding_service import (
    GeocodingServiceError,
    GeocodingServiceUnavailableError,
)
from weather.services.hourly_forecast_service import (
    HourlyForecastServiceError,
    HourlyForecastServiceUnavailableError,
)


class HourlyForecastApiTests(APITestCase):
    """
    Test the hourly forecast endpoint by city and country.
    """

    def setUp(self):
        """
        Resolve the endpoint URL and prepare reusable mock data.
        """

        self.url = reverse(
            "weather:hourly-forecast-by-city"
        )

        self.today = date.today()
        self.valid_forecast_date = self.today + timedelta(days=1)

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

        self.hourly_response = {
            "location": {
                "latitude": 48.85341,
                "longitude": 2.3488,
                "elevation": 42,
                "timezone": "Europe/Paris",
                "timezone_abbreviation": "CEST",
                "utc_offset_seconds": 7200,
            },
            "hourly": [
                {
                    "time": (
                        f"{self.valid_forecast_date.isoformat()}T00:00"
                    ),
                    "temperature": 18.2,
                    "relative_humidity": 71,
                    "apparent_temperature": 18.0,
                    "precipitation_probability": 10,
                    "precipitation": 0,
                    "rain": 0,
                    "showers": 0,
                    "snowfall": 0,
                    "weather_code": 1,
                    "cloud_cover": 20,
                    "visibility": 24000,
                    "wind_speed": 8.4,
                    "wind_direction": 210,
                    "wind_gusts": 13.2,
                    "is_day": False,
                },
                {
                    "time": (
                        f"{self.valid_forecast_date.isoformat()}T01:00"
                    ),
                    "temperature": 17.8,
                    "relative_humidity": 73,
                    "apparent_temperature": 17.5,
                    "precipitation_probability": 10,
                    "precipitation": 0,
                    "rain": 0,
                    "showers": 0,
                    "snowfall": 0,
                    "weather_code": 1,
                    "cloud_cover": 25,
                    "visibility": 24000,
                    "wind_speed": 7.9,
                    "wind_direction": 215,
                    "wind_gusts": 12.5,
                    "is_day": False,
                },
            ],
            "units": {
                "temperature": "°C",
                "relative_humidity": "%",
                "apparent_temperature": "°C",
                "precipitation_probability": "%",
                "precipitation": "mm",
                "rain": "mm",
                "showers": "mm",
                "snowfall": "cm",
                "weather_code": "wmo code",
                "cloud_cover": "%",
                "visibility": "m",
                "wind_speed": "km/h",
                "wind_direction": "°",
                "wind_gusts": "km/h",
            },
        }

    def get_valid_parameters(self):
        """
        Return valid query parameters for the hourly endpoint.
        """

        return {
            "city": "Paris",
            "country": "France",
            "forecast_date": self.valid_forecast_date.isoformat(),
        }

    @patch(
        "weather.views."
        "HourlyForecastService.get_hourly_forecast"
    )
    @patch(
        "weather.views."
        "GeocodingService.find_location_by_country_name"
    )
    def test_returns_hourly_forecast_for_valid_request(
        self,
        mocked_geocoding,
        mocked_hourly_service,
    ):
        """
        A valid city, country, and date return hourly weather data.
        """

        mocked_geocoding.return_value = self.location
        mocked_hourly_service.return_value = self.hourly_response

        response = self.client.get(
            self.url,
            self.get_valid_parameters(),
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
            self.hourly_response,
        )

        mocked_geocoding.assert_called_once_with(
            city="Paris",
            country="France",
        )

        mocked_hourly_service.assert_called_once_with(
            latitude=48.85341,
            longitude=2.3488,
            forecast_date=self.valid_forecast_date.isoformat(),
        )

    def test_returns_400_when_city_is_missing(self):
        """
        City is required.
        """

        response = self.client.get(
            self.url,
            {
                "country": "France",
                "forecast_date": (
                    self.valid_forecast_date.isoformat()
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "city",
            response.data["errors"],
        )

    def test_returns_400_when_country_is_missing(self):
        """
        Country is required.
        """

        response = self.client.get(
            self.url,
            {
                "city": "Paris",
                "forecast_date": (
                    self.valid_forecast_date.isoformat()
                ),
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

    def test_returns_400_when_forecast_date_is_missing(self):
        """
        Forecast date is required.
        """

        response = self.client.get(
            self.url,
            {
                "city": "Paris",
                "country": "France",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "forecast_date",
            response.data["errors"],
        )

    def test_returns_400_for_invalid_date_format(self):
        """
        Forecast date must use the YYYY-MM-DD format.
        """

        response = self.client.get(
            self.url,
            {
                "city": "Paris",
                "country": "France",
                "forecast_date": "01-08-2026",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "forecast_date",
            response.data["errors"],
        )

    def test_returns_400_for_past_date(self):
        """
        Forecast dates cannot be before today.
        """

        past_date = self.today - timedelta(days=1)

        response = self.client.get(
            self.url,
            {
                "city": "Paris",
                "country": "France",
                "forecast_date": past_date.isoformat(),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "forecast_date",
            response.data["errors"],
        )

    def test_returns_400_for_date_more_than_fifteen_days_ahead(self):
        """
        Forecast dates cannot exceed the supported 15-day range.
        """

        unsupported_date = self.today + timedelta(days=16)

        response = self.client.get(
            self.url,
            {
                "city": "Paris",
                "country": "France",
                "forecast_date": unsupported_date.isoformat(),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "forecast_date",
            response.data["errors"],
        )

    @patch(
        "weather.views."
        "GeocodingService.find_location_by_country_name"
    )
    def test_returns_404_when_location_is_not_found(
        self,
        mocked_geocoding,
    ):
        """
        An unknown city and country combination returns HTTP 404.
        """

        mocked_geocoding.return_value = None

        response = self.client.get(
            self.url,
            self.get_valid_parameters(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            response.data["success"]
        )

        self.assertEqual(
            response.data["error"],
            (
                "No location was found for the provided "
                "city and country."
            ),
        )

    @patch(
        "weather.views."
        "GeocodingService.find_location_by_country_name"
    )
    def test_returns_503_when_geocoding_service_is_unavailable(
        self,
        mocked_geocoding,
    ):
        """
        Geocoding connection failures return HTTP 503.
        """

        mocked_geocoding.side_effect = (
            GeocodingServiceUnavailableError(
                "The geocoding service is unavailable."
            )
        )

        response = self.client.get(
            self.url,
            self.get_valid_parameters(),
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
        Invalid geocoding provider data return HTTP 502.
        """

        mocked_geocoding.side_effect = (
            GeocodingServiceError(
                "The geocoding service returned invalid data."
            )
        )

        response = self.client.get(
            self.url,
            self.get_valid_parameters(),
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
        "HourlyForecastService.get_hourly_forecast"
    )
    @patch(
        "weather.views."
        "GeocodingService.find_location_by_country_name"
    )
    def test_returns_503_when_hourly_service_is_unavailable(
        self,
        mocked_geocoding,
        mocked_hourly_service,
    ):
        """
        Hourly weather provider connection failures return HTTP 503.
        """

        mocked_geocoding.return_value = self.location

        mocked_hourly_service.side_effect = (
            HourlyForecastServiceUnavailableError(
                "The hourly forecast service is currently unavailable."
            )
        )

        response = self.client.get(
            self.url,
            self.get_valid_parameters(),
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
            (
                "The hourly forecast service is currently "
                "unavailable."
            ),
        )

    @patch(
        "weather.views."
        "HourlyForecastService.get_hourly_forecast"
    )
    @patch(
        "weather.views."
        "GeocodingService.find_location_by_country_name"
    )
    def test_returns_502_for_invalid_hourly_response(
        self,
        mocked_geocoding,
        mocked_hourly_service,
    ):
        """
        Invalid hourly weather provider data return HTTP 502.
        """

        mocked_geocoding.return_value = self.location

        mocked_hourly_service.side_effect = (
            HourlyForecastServiceError(
                "The hourly forecast service returned invalid hourly data."
            )
        )

        response = self.client.get(
            self.url,
            self.get_valid_parameters(),
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
                "The hourly forecast service returned "
                "invalid hourly data."
            ),
        )