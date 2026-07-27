from drf_spectacular.utils import extend_schema
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

@extend_schema(
    tags=["Authentication"],
    summary="Get the authenticated user profile",
    description=(
        "Return the profile of the user identified by "
        "the JWT access token."
    ),
    responses={
        200: UserProfileSerializer,
    },
)
class ProfileView(generics.RetrieveAPIView):
    """
    Return the profile of the currently authenticated user.

    GET /api/auth/profile/
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        request.user is populated by JWTAuthentication
        after validating the Bearer access token.
        """

        return self.request.user