from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from weather.serializers import (
    CurrentWeatherQuerySerializer,
    DailyForecastByCityQuerySerializer,
    DailyForecastQuerySerializer,
    HourlyForecastByCityQuerySerializer,
    LocationSearchQuerySerializer,
)
from weather.services.geocoding_service import (
    GeocodingService,
    GeocodingServiceError,
    GeocodingServiceUnavailableError,
)
from weather.services.current_weather_service import (
    CurrentWeatherService,
    CurrentWeatherServiceError,
    CurrentWeatherServiceUnavailableError,
)
from weather.services.daily_forecast_service import (
    DailyForecastService,
    DailyForecastServiceError,
    DailyForecastServiceUnavailableError,
)
from weather.services.hourly_forecast_service import (
    HourlyForecastService,
    HourlyForecastServiceError,
    HourlyForecastServiceUnavailableError,
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
                name="forecast_date",
                description="Selected forecast date.",
                required=True,
                type={
                    "type": "string",
                    "format": "date",
                },
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        "Selected date",
                        value="2026-07-31",
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
        
        
        
class CurrentWeatherView(APIView):
    """
    Return the current weather conditions for a given
    latitude and longitude.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Get current weather",
        description=(
            "Returns the current weather conditions for the provided "
            "latitude and longitude using the Open-Meteo API."
        ),
        parameters=[
            OpenApiParameter(
                name="latitude",
                description="Latitude between -90 and 90.",
                required=True,
                type=float,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        "Paris latitude",
                        value=48.8566,
                    ),
                ],
            ),
            OpenApiParameter(
                name="longitude",
                description="Longitude between -180 and 180.",
                required=True,
                type=float,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        "Paris longitude",
                        value=2.3522,
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
                    "data": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "object",
                            },
                            "current": {
                                "type": "object",
                            },
                            "units": {
                                "type": "object",
                            },
                        },
                    },
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                    },
                    "errors": {
                        "type": "object",
                    },
                },
            },
            502: {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                    },
                    "error": {
                        "type": "string",
                    },
                },
            },
            503: {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                    },
                    "error": {
                        "type": "string",
                    },
                },
            },
        },
        tags=["Weather"],
    )
    def get(self, request):
        """
        Validate the coordinates, call the weather service,
        and return a normalized API response.
        """

        # Validate latitude and longitude from the query parameters.
        serializer = CurrentWeatherQuerySerializer(
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

        latitude = serializer.validated_data["latitude"]
        longitude = serializer.validated_data["longitude"]

        try:
            # Retrieve the current weather from Open-Meteo.
            weather_data = CurrentWeatherService.get_current_weather(
                latitude=latitude,
                longitude=longitude,
            )

        except CurrentWeatherServiceUnavailableError as exc:
            # Return 503 when the external weather service cannot be reached.
            return Response(
                {
                    "success": False,
                    "error": str(exc),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except CurrentWeatherServiceError as exc:
            # Return 502 when Open-Meteo returns an invalid response.
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
                "data": weather_data,
            },
            status=status.HTTP_200_OK,
        )
class DailyForecastView(APIView):
    """
    Return a daily weather forecast for a given latitude,
    longitude, and number of forecast days.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Get daily weather forecast",
        description=(
            "Returns a daily weather forecast for the provided "
            "latitude and longitude using the Open-Meteo API."
        ),
        parameters=[
            OpenApiParameter(
                name="latitude",
                description="Latitude between -90 and 90.",
                required=True,
                type=float,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        "Paris latitude",
                        value=48.8566,
                    ),
                ],
            ),
            OpenApiParameter(
                name="longitude",
                description="Longitude between -180 and 180.",
                required=True,
                type=float,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        "Paris longitude",
                        value=2.3522,
                    ),
                ],
            ),
            OpenApiParameter(
                name="days",
                description="Number of forecast days between 1 and 16.",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        "Seven days",
                        value=7,
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
                    "data": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "object",
                            },
                            "daily": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                },
                            },
                            "units": {
                                "type": "object",
                            },
                        },
                    },
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                    },
                    "errors": {
                        "type": "object",
                    },
                },
            },
            502: {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                    },
                    "error": {
                        "type": "string",
                    },
                },
            },
            503: {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                    },
                    "error": {
                        "type": "string",
                    },
                },
            },
        },
        tags=["Weather"],
    )
    def get(self, request):
        """
        Validate the coordinates and retrieve the daily forecast.
        """

        # Validate latitude, longitude, and forecast duration.
        serializer = DailyForecastQuerySerializer(
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

        latitude = serializer.validated_data["latitude"]
        longitude = serializer.validated_data["longitude"]
        days = serializer.validated_data["days"]

        try:
            # Retrieve the forecast from Open-Meteo.
            forecast_data = DailyForecastService.get_daily_forecast(
                latitude=latitude,
                longitude=longitude,
                days=days,
            )

        except DailyForecastServiceUnavailableError as exc:
            # Return 503 when the external weather service is unavailable.
            return Response(
                {
                    "success": False,
                    "error": str(exc),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except DailyForecastServiceError as exc:
            # Return 502 when the external service returns invalid data.
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
                "data": forecast_data,
            },
            status=status.HTTP_200_OK,
        )        
class DailyForecastByCityView(APIView):
    """
    Return a daily weather forecast using a city
    and a full country name.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Get daily forecast by city and country",
        description=(
            "Searches for a city in the specified country, resolves "
            "its coordinates, and retrieves its daily forecast."
        ),
        parameters=[
            OpenApiParameter(
                name="city",
                description="City or location name.",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        "Paris",
                        value="Paris",
                    ),
                ],
            ),
            OpenApiParameter(
                name="country",
                description="Full country name.",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        "France",
                        value="France",
                    ),
                ],
            ),
            OpenApiParameter(
                name="days",
                description="Number of forecast days between 1 and 16.",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        "Seven days",
                        value=7,
                    ),
                ],
            ),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "location": {"type": "object"},
                    "data": {"type": "object"},
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "errors": {"type": "object"},
                },
            },
            404: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "error": {"type": "string"},
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
        Resolve the city coordinates and retrieve its daily forecast.
        """

        # Validate the city, country, and forecast duration.
        serializer = DailyForecastByCityQuerySerializer(
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

        city = serializer.validated_data["city"]
        country = serializer.validated_data["country"]
        days = serializer.validated_data["days"]

        try:
            # Find a location matching both the city and country name.
            location = GeocodingService.find_location_by_country_name(
                city=city,
                country=country,
            )

            if location is None:
                return Response(
                    {
                        "success": False,
                        "error": (
                            "No location was found for the provided "
                            "city and country."
                        ),
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Retrieve the forecast using the resolved coordinates.
            forecast_data = DailyForecastService.get_daily_forecast(
                latitude=location["latitude"],
                longitude=location["longitude"],
                days=days,
            )

        except (
            GeocodingServiceUnavailableError,
            DailyForecastServiceUnavailableError,
        ) as exc:
            return Response(
                {
                    "success": False,
                    "error": str(exc),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except (
            GeocodingServiceError,
            DailyForecastServiceError,
        ) as exc:
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
                "location": location,
                "data": forecast_data,
            },
            status=status.HTTP_200_OK,
        )
        
class HourlyForecastByCityView(APIView):
    """
    Return an hourly weather forecast using a city
    and a full country name.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Get hourly forecast by city and country",
        description=(
            "Searches for a city in the specified country, resolves "
            "its coordinates, and retrieves its hourly weather forecast."
        ),
        parameters=[
            OpenApiParameter(
                name="city",
                description="City or location name.",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        "Paris",
                        value="Paris",
                    ),
                ],
            ),
            OpenApiParameter(
                name="country",
                description="Full country name.",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        "France",
                        value="France",
                    ),
                ],
            ),
            OpenApiParameter(
                name="forecast_date",
                description="Selected forecast date in YYYY-MM-DD format.",
                required=True,
                type={
                    "type": "string",
                    "format": "date",
                },
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        "Selected date",
                        value="2026-07-31",
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
                    "location": {
                        "type": "object",
                    },
                    "data": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "object",
                            },
                            "hourly": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                },
                            },
                            "units": {
                                "type": "object",
                            },
                        },
                    },
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                    },
                    "errors": {
                        "type": "object",
                    },
                },
            },
            404: {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                    },
                    "error": {
                        "type": "string",
                    },
                },
            },
            502: {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                    },
                    "error": {
                        "type": "string",
                    },
                },
            },
            503: {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                    },
                    "error": {
                        "type": "string",
                    },
                },
            },
        },
        tags=["Weather"],
    )
    def get(self, request):
        """
        Resolve the city coordinates and retrieve its hourly forecast.
        """

        # Validate the city, country, and forecast duration.
        serializer = HourlyForecastByCityQuerySerializer(
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

        city = serializer.validated_data["city"]
        country = serializer.validated_data["country"]
        forecast_date = serializer.validated_data["forecast_date"]

        try:
            # Find a location matching both the city and country name.
            location = GeocodingService.find_location_by_country_name(
                city=city,
                country=country,
            )

            if location is None:
                return Response(
                    {
                        "success": False,
                        "error": (
                            "No location was found for the provided "
                            "city and country."
                        ),
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Retrieve the hourly forecast using the resolved coordinates.
            forecast_data = HourlyForecastService.get_hourly_forecast(
                latitude=location["latitude"],
                longitude=location["longitude"],
                forecast_date=forecast_date.isoformat(),
            )

        except (
            GeocodingServiceUnavailableError,
            HourlyForecastServiceUnavailableError,
        ) as exc:
            # Return 503 when an external service cannot be reached.
            return Response(
                {
                    "success": False,
                    "error": str(exc),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except (
            GeocodingServiceError,
            HourlyForecastServiceError,
        ) as exc:
            # Return 502 when an external service returns invalid data.
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
                "location": location,
                "data": forecast_data,
            },
            status=status.HTTP_200_OK,
        )