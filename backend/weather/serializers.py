from datetime import date, timedelta

from rest_framework import serializers

from weather.models import FavoriteCity


class FavoriteCitySerializer(serializers.ModelSerializer):
    """
    Serialize a favorite city owned by the authenticated user.
    """

    class Meta:
        model = FavoriteCity
        fields = [
            "id",
            "city",
            "country",
            "latitude",
            "longitude",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]

    def validate_city(self, value):
        """
        Normalize and validate the city name.
        """

        city = value.strip()

        if not city:
            raise serializers.ValidationError(
                "City cannot be empty."
            )

        return city

    def validate_country(self, value):
        """
        Normalize and validate the country name.
        """

        country = value.strip()

        if not country:
            raise serializers.ValidationError(
                "Country cannot be empty."
            )

        return country

    def validate(self, attrs):
        """
        Prevent the authenticated user from saving a duplicate city.
        """

        request = self.context.get("request")

        if request is None or not request.user.is_authenticated:
            return attrs

        city = attrs.get("city")
        country = attrs.get("country")

        duplicate_exists = FavoriteCity.objects.filter(
            user=request.user,
            city__iexact=city,
            country__iexact=country,
        ).exists()

        if duplicate_exists:
            raise serializers.ValidationError(
                {
                    "city": (
                        "This city is already present in your favorites."
                    ),
                }
            )

        return attrs


class LocationSearchQuerySerializer(serializers.Serializer):
    """
    Validate the query parameters used to search for locations.

    Example:
        GET /api/weather/locations/search/?query=Paris
    """

    query = serializers.CharField(
        required=True,
        allow_blank=False,
        min_length=2,
        max_length=100,
        trim_whitespace=True,
        help_text="City or location name to search for.",
    )

    def validate_query(self, value: str) -> str:
        """
        Normalize and validate the location search query.
        """

        cleaned_value = value.strip()

        if not cleaned_value:
            raise serializers.ValidationError(
                "The search query cannot be empty."
            )

        return cleaned_value


class CurrentWeatherQuerySerializer(serializers.Serializer):
    """
    Validate the coordinates used to retrieve current weather data.
    """

    latitude = serializers.FloatField(
        required=True,
        min_value=-90,
        max_value=90,
        help_text="Latitude between -90 and 90.",
    )

    longitude = serializers.FloatField(
        required=True,
        min_value=-180,
        max_value=180,
        help_text="Longitude between -180 and 180.",
    )


class ReverseGeocodingQuerySerializer(serializers.Serializer):
    """
    Validate the coordinates used to resolve a location name.
    """

    latitude = serializers.FloatField(
        required=True,
        min_value=-90,
        max_value=90,
        help_text="Latitude between -90 and 90.",
    )

    longitude = serializers.FloatField(
        required=True,
        min_value=-180,
        max_value=180,
        help_text="Longitude between -180 and 180.",
    )


class DailyForecastQuerySerializer(serializers.Serializer):
    """
    Validate the coordinates and number of forecast days
    used to retrieve the daily weather forecast.
    """

    latitude = serializers.FloatField(
        required=True,
        min_value=-90,
        max_value=90,
        help_text="Latitude between -90 and 90.",
    )

    longitude = serializers.FloatField(
        required=True,
        min_value=-180,
        max_value=180,
        help_text="Longitude between -180 and 180.",
    )

    days = serializers.IntegerField(
        required=False,
        default=7,
        min_value=1,
        max_value=16,
        help_text="Number of forecast days between 1 and 16.",
    )


class DailyForecastByCityQuerySerializer(serializers.Serializer):
    """
    Validate the city, country name, and forecast duration
    used to retrieve a daily weather forecast.
    """

    city = serializers.CharField(
        required=True,
        allow_blank=False,
        min_length=2,
        max_length=100,
        trim_whitespace=True,
        help_text="City or location name, for example Paris.",
    )

    country = serializers.CharField(
        required=True,
        allow_blank=False,
        min_length=2,
        max_length=100,
        trim_whitespace=True,
        help_text="Full country name, for example France.",
    )

    days = serializers.IntegerField(
        required=False,
        default=7,
        min_value=1,
        max_value=16,
        help_text="Number of forecast days between 1 and 16.",
    )

    def validate_city(self, value: str) -> str:
        """
        Remove unnecessary whitespace from the city name.
        """

        return value.strip()

    def validate_country(self, value: str) -> str:
        """
        Remove unnecessary whitespace from the country name.
        """

        return value.strip()


class HourlyForecastQuerySerializer(serializers.Serializer):
    """
    Validate the coordinates and selected forecast date
    used to retrieve an hourly weather forecast.
    """

    latitude = serializers.FloatField(
        required=True,
        min_value=-90,
        max_value=90,
        help_text="Latitude between -90 and 90.",
    )

    longitude = serializers.FloatField(
        required=True,
        min_value=-180,
        max_value=180,
        help_text="Longitude between -180 and 180.",
    )

    forecast_date = serializers.DateField(
        required=True,
        help_text="Forecast date in YYYY-MM-DD format.",
    )

    def validate_forecast_date(self, value: date) -> date:
        """
        Ensure that the selected date is within the supported forecast range.
        """

        today = date.today()
        maximum_date = today + timedelta(days=15)

        if value < today:
            raise serializers.ValidationError(
                "The forecast date cannot be in the past."
            )

        if value > maximum_date:
            raise serializers.ValidationError(
                "The forecast date cannot be more than 15 days ahead."
            )

        return value


class HourlyForecastByCityQuerySerializer(serializers.Serializer):
    """
    Validate the city, country, and selected forecast date
    used to retrieve an hourly weather forecast.
    """

    city = serializers.CharField(
        required=True,
        allow_blank=False,
        min_length=2,
        max_length=100,
        trim_whitespace=True,
        help_text="City or location name, for example Paris.",
    )

    country = serializers.CharField(
        required=True,
        allow_blank=False,
        min_length=2,
        max_length=100,
        trim_whitespace=True,
        help_text="Full country name, for example France.",
    )

    forecast_date = serializers.DateField(
        required=True,
        help_text="Forecast date in YYYY-MM-DD format.",
    )

    def validate_city(self, value: str) -> str:
        """
        Remove unnecessary whitespace from the city name.
        """

        return value.strip()

    def validate_country(self, value: str) -> str:
        """
        Remove unnecessary whitespace from the country name.
        """

        return value.strip()

    def validate_forecast_date(self, value: date) -> date:
        """
        Ensure that the selected date is within the supported forecast range.
        """

        today = date.today()
        maximum_date = today + timedelta(days=15)

        if value < today:
            raise serializers.ValidationError(
                "The forecast date cannot be in the past."
            )

        if value > maximum_date:
            raise serializers.ValidationError(
                "The forecast date cannot be more than 15 days ahead."
            )

        return value


class HistoricalWeatherByCityQuerySerializer(serializers.Serializer):
    """
    Validate the city, country, and date range
    used to retrieve historical weather data.
    """

    city = serializers.CharField(
        required=True,
        allow_blank=False,
        min_length=2,
        max_length=100,
        trim_whitespace=True,
        help_text="City or location name, for example Paris.",
    )

    country = serializers.CharField(
        required=True,
        allow_blank=False,
        min_length=2,
        max_length=100,
        trim_whitespace=True,
        help_text="Full country name, for example France.",
    )

    start_date = serializers.DateField(
        required=True,
        help_text="Start date in YYYY-MM-DD format.",
    )

    end_date = serializers.DateField(
        required=True,
        help_text="End date in YYYY-MM-DD format.",
    )

    def validate_city(self, value: str) -> str:
        """
        Remove unnecessary whitespace from the city name.
        """

        return value.strip()

    def validate_country(self, value: str) -> str:
        """
        Remove unnecessary whitespace from the country name.
        """

        return value.strip()

    def validate(self, attrs):
        """
        Validate the requested historical date range.
        """

        start_date = attrs["start_date"]
        end_date = attrs["end_date"]
        today = date.today()

        if start_date > end_date:
            raise serializers.ValidationError(
                {
                    "end_date": (
                        "The end date must be greater than or equal "
                        "to the start date."
                    )
                }
            )

        if end_date >= today:
            raise serializers.ValidationError(
                {
                    "end_date": (
                        "Historical weather dates must be before today."
                    )
                }
            )

        # Limit one request to one year to keep responses manageable.
        if (end_date - start_date).days > 366:
            raise serializers.ValidationError(
                {
                    "end_date": (
                        "The historical date range cannot exceed 366 days."
                    )
                }
            )

        return attrs