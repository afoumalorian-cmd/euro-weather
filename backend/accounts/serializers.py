from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer responsible for creating a new user account.

    It validates:
    - the uniqueness of the email address;
    - the password confirmation;
    - the minimum password length.
    """

    # This field is only accepted in requests.
    # It will never be returned in an API response.
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    # Used only to confirm that the user entered
    # the intended password correctly.
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        )
        read_only_fields = ("id",)

    def validate_email(self, value):
        """
        Normalize the email and ensure that it is unique.
        """

        normalized_email = value.strip().lower()

        if User.objects.filter(
            email__iexact=normalized_email
        ).exists():
            raise serializers.ValidationError(
                "An account already exists with this email address."
            )

        return normalized_email

    def validate(self, attrs):
        """
        Ensure that password and password_confirm are identical.
        """

        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {
                    "password_confirm": (
                        "The two passwords do not match."
                    )
                }
            )

        return attrs

    def create(self, validated_data):
        """
        Create the user using Django's create_user method.

        create_user hashes the password before storing it.
        The plain password is never saved in PostgreSQL.
        """

        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer used to return the authenticated user's profile.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
        )

        # The profile endpoint is currently read-only.
        read_only_fields = fields