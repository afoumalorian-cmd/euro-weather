from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


urlpatterns = [
    # Django administration interface.
    path(
        "admin/",
        admin.site.urls,
    ),

    # Account and authentication endpoints.
    path(
        "api/auth/",
        include("accounts.urls"),
    ),

    # Raw OpenAPI schema in YAML/JSON format.
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="api-schema",
    ),

    # Interactive Swagger interface.
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="api-schema"
        ),
        name="swagger-ui",
    ),

    # Alternative API documentation interface.
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(
            url_name="api-schema"
        ),
        name="redoc",
    ),
]