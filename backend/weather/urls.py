from django.urls import path

from weather.views import CurrentWeatherView, LocationSearchView
from weather.views import LocationSearchView


app_name = "weather"

urlpatterns = [
    path(
        "locations/search/",
        LocationSearchView.as_view(),
        name="location-search",
    ),
    path(
        "current/",
        CurrentWeatherView.as_view(),
        name="current-weather",
    ),
]
