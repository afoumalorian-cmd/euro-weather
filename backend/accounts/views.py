from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated


from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
)


@extend_schema(
    tags=["Authentication"],
    summary="Register a new user",
    description=(
        "Create a new user account using a unique username "
        "and email address."
    ),
    request=RegisterSerializer,
    responses={
        201: RegisterSerializer,
    },

    # Registration is public, so Swagger does not display
    # JWT authentication as required for this endpoint.
    auth=[],
)
class RegisterView(generics.CreateAPIView):
    """
    Public endpoint used to create a new user account.

    POST /api/auth/register/
    """

    serializer_class = RegisterSerializer

    # Anyone can create an account without being connected.
    permission_classes = [AllowAny]

    # Completely ignore authentication headers on this public endpoint.
    # This also prevents an invalid JWT header from blocking registration.
    authentication_classes = []


@extend_schema_view(
    get=extend_schema(
        tags=["Authentication"],
        summary="Get the authenticated user profile",
        responses={
            200: UserProfileSerializer,
        },
    ),
    put=extend_schema(
        tags=["Authentication"],
        summary="Replace the authenticated user profile",
        request=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
        },
    ),
    patch=extend_schema(
        tags=["Authentication"],
        summary="Update the authenticated user profile",
        request=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
        },
    ),
)
class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the authenticated user's profile.

    GET /api/auth/profile/
    PUT /api/auth/profile/
    PATCH /api/auth/profile/
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Return the user authenticated by the JWT access token.
        """

        return self.request.user