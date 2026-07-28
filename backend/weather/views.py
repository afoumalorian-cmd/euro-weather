from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from weather.serializers import LocationSearchQuerySerializer
from weather.services.geocoding_service import (
    GeocodingService,
    GeocodingServiceError,
    GeocodingServiceUnavailableError,
)


class LocationSearchView(APIView):
    """
    Recherche des villes et localisations avec Open-Meteo.

    Cet endpoint est public afin que l'utilisateur puisse rechercher
    une ville sans être obligatoirement connecté.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Search for a location",
        description=(
            "Searches for cities and locations using the Open-Meteo "
            "Geocoding API."
        ),
        parameters=[
            OpenApiParameter(
                name="query",
                description="City or location name to search for.",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        "Paris",
                        value="Paris",
                    ),
                    OpenApiExample(
                        "London",
                        value="London",
                    ),
                ],
            ),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                    },
                    "count": {
                        "type": "integer",
                    },
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                                "latitude": {"type": "number"},
                                "longitude": {"type": "number"},
                                "elevation": {"type": "number"},
                                "timezone": {"type": "string"},
                                "country": {"type": "string"},
                                "country_code": {"type": "string"},
                                "admin1": {"type": "string"},
                                "admin2": {"type": "string"},
                                "population": {"type": "integer"},
                            },
                        },
                    },
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "errors": {"type": "object"},
                },
            },
            502: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "error": {"type": "string"},
                },
            },
            503: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "error": {"type": "string"},
                },
            },
        },
        tags=["Weather"],
    )
    def get(self, request):
        """
        Valide le paramètre query, appelle le service Open-Meteo
        et retourne une réponse normalisée.
        """

        serializer = LocationSearchQuerySerializer(
            data=request.query_params
        )

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        query = serializer.validated_data["query"]

        try:
            locations = GeocodingService.search_locations(
                query=query,
            )

        except GeocodingServiceUnavailableError as exc:
            # L'API externe ne répond pas ou le délai est dépassé.
            return Response(
                {
                    "success": False,
                    "error": str(exc),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except GeocodingServiceError as exc:
            # Open-Meteo a répondu, mais avec une réponse invalide
            # ou une erreur HTTP.
            return Response(
                {
                    "success": False,
                    "error": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                "success": True,
                "count": len(locations),
                "results": locations,
            },
            status=status.HTTP_200_OK,
        )