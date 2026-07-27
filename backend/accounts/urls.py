from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import ProfileView, RegisterView


urlpatterns = [
    # Create a new account.
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),

    # Authenticate with username and password.
    # Returns an access token and a refresh token.
    path(
        "login/",
        TokenObtainPairView.as_view(),
        name="login",
    ),

    # Generate a new access token using a refresh token.
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),

    # Return the connected user's information.
    path(
        "profile/",
        ProfileView.as_view(),
        name="profile",
    ),
]