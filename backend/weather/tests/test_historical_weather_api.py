from datetime import date, timedelta
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from weather.services.geocoding_service import (
    GeocodingServiceError,
    GeocodingServiceUnavailableError,
)
from weather.services.historical_weather_service import (
    HistoricalWeatherServiceError,
    HistoricalWeatherServiceUnavailableError,
)


class HistoricalWeatherApiTests(APITestCase):
    """
    Test the historical weather endpoint by city and country.
    """

    def setUp(self):
        """
        Resolve the endpoint URL and prepare reusable test data.
        """

        self.url = reverse(
            "weather:historical-weather-by-city"
        )

        self.end_date = date.today() - timedelta(days=1)
        self.start_date = self.end_date - timedelta(days=6)

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

        self.historical_response = {
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
                    "date": self.start_date.isoformat(),
                    "weather_code": 2,
                    "temperature_max": 24.5,
                    "temperature_min": 15.2,
                    "temperature_mean": 19.6,
                    "apparent_temperature_max": 25.1,
                    "apparent_temperature_min": 14.8,
                    "precipitation_sum": 1.2,
                    "rain_sum": 1.2,
                    "snowfall_sum": 0,
                    "precipitation_hours": 2,
                    "wind_speed_max": 18.4,
                    "wind_gusts_max": 31.7,
                    "wind_direction_dominant": 220,
                    "sunrise": (
                        f"{self.start_date.isoformat()}T06:25"
                    ),
                    "sunset": (
                        f"{self.start_date.isoformat()}T21:20"
                    ),
                },
            ],
            "units": {
                "weather_code": "wmo code",
                "temperature_max": "°C",
                "temperature_min": "°C",
                "temperature_mean": "°C",
                "apparent_temperature_max": "°C",
                "apparent_temperature_min": "°C",
                "precipitation_sum": "mm",
                "rain_sum": "mm",
                "snowfall_sum": "cm",
                "precipitation_hours": "h",
                "wind_speed_max": "km/h",
                "wind_gusts_max": "km/h",
                "wind_direction_dominant": "°",
                "sunrise": "iso8601",
                "sunset": "iso8601",
            },
        }

    def get_valid_parameters(self):
        """
        Return valid historical weather query parameters.
        """

        return {
            "city": "Paris",
            "country": "France",
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
        }

    @patch(
        "weather.views."
        "HistoricalWeatherService.get_historical_weather"
    )
    @patch(
        "weather.views."
        "GeocodingService.find_location_by_country_name"
    )
    def test_returns_historical_weather_for_valid_request(
        self,
        mocked_geocoding,
        mocked_historical_service,
    ):
        """
        Valid parameters return normalized historical weather data.
        """

        mocked_geocoding.return_value = self.location
        mocked_historical_service.return_value = (
            self.historical_response
        )

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
            self.historical_response,
        )

        mocked_geocoding.assert_called_once_with(
            city="Paris",
            country="France",
        )

        mocked_historical_service.assert_called_once_with(
            latitude=48.85341,
            longitude=2.3488,
            start_date=self.start_date.isoformat(),
            end_date=self.end_date.isoformat(),
        )

    def test_returns_400_when_city_is_missing(self):
        """
        City is required.
        """

        parameters = self.get_valid_parameters()
        parameters.pop("city")

        response = self.client.get(
            self.url,
            parameters,
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

        parameters = self.get_valid_parameters()
        parameters.pop("country")

        response = self.client.get(
            self.url,
            parameters,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "country",
            response.data["errors"],
        )

    def test_returns_400_when_start_date_is_missing(self):
        """
        Start date is required.
        """

        parameters = self.get_valid_parameters()
        parameters.pop("start_date")

        response = self.client.get(
            self.url,
            parameters,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "start_date",
            response.data["errors"],
        )

    def test_returns_400_when_end_date_is_missing(self):
        """
        End date is required.
        """

        parameters = self.get_valid_parameters()
        parameters.pop("end_date")

        response = self.client.get(
            self.url,
            parameters,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "end_date",
            response.data["errors"],
        )

    def test_returns_400_for_invalid_date_format(self):
        """
        Historical dates must use YYYY-MM-DD format.
        """

        parameters = self.get_valid_parameters()
        parameters["start_date"] = "01-07-2026"

        response = self.client.get(
            self.url,
            parameters,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "start_date",
            response.data["errors"],
        )

    def test_returns_400_when_start_date_is_after_end_date(self):
        """
        Start date cannot be later than end date.
        """

        response = self.client.get(
            self.url,
            {
                "city": "Paris",
                "country": "France",
                "start_date": self.end_date.isoformat(),
                "end_date": self.start_date.isoformat(),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "end_date",
            response.data["errors"],
        )

    def test_returns_400_when_end_date_is_today(self):
        """
        Historical weather dates must be before today.
        """

        parameters = self.get_valid_parameters()
        parameters["end_date"] = date.today().isoformat()

        response = self.client.get(
            self.url,
            parameters,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "end_date",
            response.data["errors"],
        )

    def test_returns_400_when_end_date_is_in_the_future(self):
        """
        Future dates are not accepted by the historical endpoint.
        """

        parameters = self.get_valid_parameters()
        parameters["end_date"] = (
            date.today() + timedelta(days=1)
        ).isoformat()

        response = self.client.get(
            self.url,
            parameters,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "end_date",
            response.data["errors"],
        )

    def test_returns_400_when_date_range_exceeds_366_days(self):
        """
        A single historical request cannot exceed 366 days.
        """

        long_start_date = (
            self.end_date - timedelta(days=367)
        )

        response = self.client.get(
            self.url,
            {
                "city": "Paris",
                "country": "France",
                "start_date": long_start_date.isoformat(),
                "end_date": self.end_date.isoformat(),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "end_date",
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
        "HistoricalWeatherService.get_historical_weather"
    )
    @patch(
        "weather.views."
        "GeocodingService.find_location_by_country_name"
    )
    def test_returns_503_when_historical_service_is_unavailable(
        self,
        mocked_geocoding,
        mocked_historical_service,
    ):
        """
        Historical weather provider failures return HTTP 503.
        """

        mocked_geocoding.return_value = self.location

        mocked_historical_service.side_effect = (
            HistoricalWeatherServiceUnavailableError(
                "The historical weather service is currently unavailable."
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
                "The historical weather service is currently "
                "unavailable."
            ),
        )

    @patch(
        "weather.views."
        "HistoricalWeatherService.get_historical_weather"
    )
    @patch(
        "weather.views."
        "GeocodingService.find_location_by_country_name"
    )
    def test_returns_502_for_invalid_historical_response(
        self,
        mocked_geocoding,
        mocked_historical_service,
    ):
        """
        Invalid historical weather data return HTTP 502.
        """

        mocked_geocoding.return_value = self.location

        mocked_historical_service.side_effect = (
            HistoricalWeatherServiceError(
                "The historical weather service returned invalid daily data."
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
                "The historical weather service returned "
                "invalid daily data."
            ),
        )