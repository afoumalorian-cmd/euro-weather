from rest_framework import serializers


class LocationSearchQuerySerializer(serializers.Serializer):
    """
    Valide les paramètres reçus par l'endpoint de recherche de lieux.

    Exemple :
        GET /api/weather/locations/search/?query=Paris
    """

    query = serializers.CharField(
        required=True,
        allow_blank=False,
        min_length=2,
        max_length=100,
        trim_whitespace=True,
        help_text="Nom de la ville ou du lieu à rechercher.",
    )

    def validate_query(self, value: str) -> str:
        """
        Nettoie et valide la valeur du paramètre query.
        """

        cleaned_value = value.strip()

        # Empêche les recherches composées uniquement d'espaces.
        if not cleaned_value:
            raise serializers.ValidationError(
                "The search query cannot be empty."
            )

        return cleaned_value