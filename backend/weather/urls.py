from django.urls import path

from weather.views import (
    CurrentWeatherView,
    DailyForecastByCityView,
    DailyForecastView,
    LocationSearchView,
)


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
    path(
        "forecast/daily/",
        DailyForecastView.as_view(),
        name="daily-forecast",
    ),
    path(
        "forecast/daily/by-city/",
        DailyForecastByCityView.as_view(),
        name="daily-forecast-by-city",
    ),
]
