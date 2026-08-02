import unicodedata
from typing import Any

import requests


class GeocodingServiceError(Exception):
    """
    Base exception raised when the geocoding service
    cannot return valid location data.
    """


class GeocodingServiceUnavailableError(GeocodingServiceError):
    """
    Exception raised when the Open-Meteo Geocoding API
    is unavailable or does not respond before the timeout.
    """


class GeocodingService:
    """
    Retrieve and normalize location data from
    the Open-Meteo Geocoding API.
    """

    BASE_URL = "https://geocoding-api.open-meteo.com/v1/search"
    
    REQUEST_TIMEOUT = 10
    
    REVERSE_BASE_URL = (
        "https://nominatim.openstreetmap.org/reverse"
    )

    REQUEST_HEADERS = {
        "User-Agent": (
            "EuroWeather/1.0 "
            "(https://euro-weather.onrender.com)"
        ),
    }

    @classmethod
    def reverse_geocode(
        cls,
        latitude: float,
        longitude: float,
        language: str = "en",
    ) -> dict[str, Any]:
        """
        Resolve geographic coordinates into a city and country.

        Args:
            latitude:
                Latitude between -90 and 90.

            longitude:
                Longitude between -180 and 180.

            language:
                Preferred language for the returned location names.

        Returns:
            A normalized dictionary containing the resolved
            city, country, and coordinates.

        Raises:
            GeocodingServiceUnavailableError:
                When the reverse geocoding provider cannot be reached.

            GeocodingServiceError:
                When the provider returns invalid location data.
        """

        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "jsonv2",
            "addressdetails": 1,
            "accept-language": language,
            "zoom": 10,
        }

        try:
            response = requests.get(
                cls.REVERSE_BASE_URL,
                params=params,
                headers=cls.REQUEST_HEADERS,
                timeout=cls.REQUEST_TIMEOUT,
            )

            response.raise_for_status()

        except requests.Timeout as exc:
            raise GeocodingServiceUnavailableError(
                "The reverse location service did not respond in time."
            ) from exc

        except requests.ConnectionError as exc:
            raise GeocodingServiceUnavailableError(
                "The reverse location service is currently unavailable."
            ) from exc

        except requests.HTTPError as exc:
            raise GeocodingServiceError(
                "The reverse location service returned an HTTP error."
            ) from exc

        except requests.RequestException as exc:
            raise GeocodingServiceError(
                "An unexpected error occurred while contacting "
                "the reverse location service."
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise GeocodingServiceError(
                "The reverse location service returned invalid JSON."
            ) from exc

        address = payload.get("address")

        if not isinstance(address, dict):
            raise GeocodingServiceError(
                "The reverse location service returned invalid address data."
            )

        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("municipality")
            or address.get("county")
        )

        country = address.get("country")

        if not city or not country:
            raise GeocodingServiceError(
                "The city or country could not be resolved "
                "from these coordinates."
            )

        return {
            "name": city,
            "country": country,
            "country_code": address.get("country_code"),
            "state": address.get("state"),
            "county": address.get("county"),
            "postcode": address.get("postcode"),
            "latitude": latitude,
            "longitude": longitude,
            "display_name": payload.get("display_name"),
            "attribution": payload.get("licence"),
        }

    @classmethod
    def search_locations(
        cls,
        query: str,
        count: int = 10,
        language: str = "en",
    ) -> list[dict[str, Any]]:
        """
        Search for locations matching the provided query.

        Args:
            query:
                City or location name.

            count:
                Maximum number of results requested from Open-Meteo.

            language:
                Language used for location names and country names.

        Returns:
            A list of normalized locations.

        Raises:
            GeocodingServiceUnavailableError:
                When Open-Meteo cannot be reached.

            GeocodingServiceError:
                When Open-Meteo returns invalid data.
        """

        params = {
            "name": query,
            "count": count,
            "language": language,
            "format": "json",
        }

        try:
            response = requests.get(
                cls.BASE_URL,
                params=params,
                timeout=cls.REQUEST_TIMEOUT,
            )

            response.raise_for_status()

        except requests.Timeout as exc:
            raise GeocodingServiceUnavailableError(
                "The location service did not respond in time."
            ) from exc

        except requests.ConnectionError as exc:
            raise GeocodingServiceUnavailableError(
                "The location service is currently unavailable."
            ) from exc

        except requests.HTTPError as exc:
            raise GeocodingServiceError(
                "The location service returned an HTTP error."
            ) from exc

        except requests.RequestException as exc:
            raise GeocodingServiceError(
                "An unexpected error occurred while contacting "
                "the location service."
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise GeocodingServiceError(
                "The location service returned invalid JSON."
            ) from exc

        results = payload.get("results", [])

        # Open-Meteo may omit the results field when no match is found.
        if not isinstance(results, list):
            raise GeocodingServiceError(
                "The location service returned an invalid result format."
            )

        return [
            cls._normalize_location(location)
            for location in results
            if isinstance(location, dict)
        ]

    @classmethod
    def find_location_by_country_name(
        cls,
        city: str,
        country: str,
    ) -> dict[str, Any] | None:
        """
        Return the best location matching a city and country name.

        Args:
            city:
                City or location name.

            country:
                Full country name entered by the user.

        Returns:
            The best matching normalized location, or None when
            no matching location is found.
        """

        # Request several ranked results because the same city name
        # may exist in multiple countries.
        locations = cls.search_locations(
            query=city,
            count=100,
            language="en",
        )

        normalized_country = cls._normalize_text(country)

        for location in locations:
            location_country = location.get("country")

            if not isinstance(location_country, str):
                continue

            if cls._normalize_text(location_country) == normalized_country:
                return location

        return None

    @staticmethod
    def _normalize_location(
        location: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Convert an Open-Meteo location into a stable structure
        controlled by this API.
        """

        return {
            "id": location.get("id"),
            "name": location.get("name"),
            "latitude": location.get("latitude"),
            "longitude": location.get("longitude"),
            "elevation": location.get("elevation"),
            "timezone": location.get("timezone"),
            "country": location.get("country"),
            "country_code": location.get("country_code"),
            "admin1": location.get("admin1"),
            "admin2": location.get("admin2"),
            "population": location.get("population"),
        }

    @staticmethod
    def _normalize_text(value: str) -> str:
        """
        Normalize text for case-insensitive and accent-insensitive comparison.
        """

        normalized_value = unicodedata.normalize(
            "NFKD",
            value.strip(),
        )

        without_accents = "".join(
            character
            for character in normalized_value
            if not unicodedata.combining(character)
        )

        return without_accents.casefold()