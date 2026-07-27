from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
)


class RegisterView(generics.CreateAPIView):
    """
    Public endpoint used to create a new user account.

    POST /api/auth/register/
    """

    serializer_class = RegisterSerializer

    # A visitor must be able to register without
    # already having an authentication token.
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveAPIView):
    """
    Return the profile of the currently authenticated user.

    GET /api/auth/profile/
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        request.user is populated from the JWT access token.
        """

        return self.request.user