from typing import Any

import requests


class GeocodingServiceError(Exception):
    """
    Exception générique levée lorsqu'une erreur survient pendant
    la communication avec l'API de géocodage Open-Meteo.
    """


class GeocodingServiceUnavailableError(GeocodingServiceError):
    """
    Exception levée lorsque l'API Open-Meteo est temporairement
    indisponible ou inaccessible.
    """


class GeocodingService:
    """
    Service responsable de la communication avec
    l'API de géocodage Open-Meteo.
    """

    BASE_URL = "https://geocoding-api.open-meteo.com/v1/search"
    REQUEST_TIMEOUT = 10

    @classmethod
    def search_locations(
        cls,
        query: str,
        count: int = 5,
        language: str = "en",
    ) -> list[dict[str, Any]]:
        """
        Recherche des lieux correspondant au texte fourni.

        Args:
            query:
                Nom de la ville ou du lieu recherché.

            count:
                Nombre maximal de résultats demandés à Open-Meteo.

            language:
                Langue utilisée pour les résultats.

        Returns:
            Une liste de lieux normalisés.

        Raises:
            GeocodingServiceUnavailableError:
                Lorsque l'API externe est inaccessible.

            GeocodingServiceError:
                Lorsque la réponse reçue est invalide.
        """

        params = {
            # Open-Meteo attend "name", tandis que notre API expose "query".
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

            # Déclenche une exception pour les réponses HTTP 4xx ou 5xx.
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
                "The location service returned an invalid JSON response."
            ) from exc

        results = payload.get("results", [])

        # Open-Meteo peut ne pas retourner la clé "results"
        # lorsqu'aucune ville n'a été trouvée.
        if not isinstance(results, list):
            raise GeocodingServiceError(
                "The location service returned an invalid result format."
            )

        return [
            cls._normalize_location(location)
            for location in results
        ]

    @staticmethod
    def _normalize_location(
        location: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Transforme la réponse Open-Meteo en une structure stable
        contrôlée par notre propre API.
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