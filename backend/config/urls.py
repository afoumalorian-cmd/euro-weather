from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    # Django administration interface.
    path("admin/", admin.site.urls),

    # All account-related API endpoints.
    path("api/auth/", include("accounts.urls")),
]