from unittest.mock import Mock, patch

from django.core.cache import cache
from django.test import SimpleTestCase

from weather.services.geocoding_service import GeocodingService


class GeocodingServiceCacheTests(SimpleTestCase):
    """
    Test the cache behavior of the geocoding service.
    """

    def setUp(self) -> None:
        """
        Clear the cache before each test.
        """
        cache.clear()

    @patch("weather.services.geocoding_service.requests.get")
    def test_identical_location_searches_use_cached_response(
        self,
        mock_get: Mock,
    ) -> None:
        """
        Ensure identical location searches call Open-Meteo only once.
        """
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "results": [
                {
                    "id": 2988507,
                    "name": "Paris",
                    "latitude": 48.85341,
                    "longitude": 2.3488,
                    "elevation": 42.0,
                    "timezone": "Europe/Paris",
                    "country": "France",
                    "country_code": "FR",
                    "admin1": "Île-de-France",
                    "admin2": "Paris",
                    "population": 2138551,
                }
            ]
        }
        mock_get.return_value = mock_response

        first_result = GeocodingService.search_locations(
            query="Paris",
            count=10,
            language="en",
        )

        second_result = GeocodingService.search_locations(
            query="Paris",
            count=10,
            language="en",
        )

        self.assertEqual(first_result, second_result)
        self.assertEqual(mock_get.call_count, 1)

    @patch("weather.services.geocoding_service.requests.get")
    def test_different_search_parameters_use_different_cache_entries(
        self,
        mock_get: Mock,
    ) -> None:
        """
        Ensure different search parameters do not share cache entries.
        """
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        GeocodingService.search_locations(
            query="Paris",
            count=10,
            language="en",
        )

        GeocodingService.search_locations(
            query="Paris",
            count=5,
            language="en",
        )

        self.assertEqual(mock_get.call_count, 2)

    @patch("weather.services.geocoding_service.requests.get")
    def test_identical_reverse_geocoding_requests_use_cache(
        self,
        mock_get: Mock,
    ) -> None:
        """
        Ensure identical reverse geocoding requests call Nominatim once.
        """
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "display_name": "Paris, France",
            "licence": "OpenStreetMap contributors",
            "address": {
                "city": "Paris",
                "country": "France",
                "country_code": "fr",
                "state": "Île-de-France",
                "county": "Paris",
                "postcode": "75001",
            },
        }
        mock_get.return_value = mock_response

        first_result = GeocodingService.reverse_geocode(
            latitude=48.8566,
            longitude=2.3522,
            language="en",
        )

        second_result = GeocodingService.reverse_geocode(
            latitude=48.8566,
            longitude=2.3522,
            language="en",
        )

        self.assertEqual(first_result, second_result)
        self.assertEqual(mock_get.call_count, 1)

    @patch("weather.services.geocoding_service.requests.get")
    def test_different_reverse_geocoding_languages_use_different_entries(
        self,
        mock_get: Mock,
    ) -> None:
        """
        Ensure different languages do not share reverse geocoding entries.
        """
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "display_name": "Paris, France",
            "address": {
                "city": "Paris",
                "country": "France",
            },
        }
        mock_get.return_value = mock_response

        GeocodingService.reverse_geocode(
            latitude=48.8566,
            longitude=2.3522,
            language="en",
        )

        GeocodingService.reverse_geocode(
            latitude=48.8566,
            longitude=2.3522,
            language="fr",
        )

        self.assertEqual(mock_get.call_count, 2)