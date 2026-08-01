from django.urls import path

from weather.views import (
    CurrentWeatherView,
    DailyForecastByCityView,
    DailyForecastView,
    FavoriteCityDetailView,
    FavoriteCityListCreateView,
    HistoricalWeatherByCityView,
    HourlyForecastByCityView,
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
    path(
        "forecast/hourly/by-city/",
        HourlyForecastByCityView.as_view(),
        name="hourly-forecast-by-city",
    ),
    path(
        "history/by-city/",
        HistoricalWeatherByCityView.as_view(),
        name="historical-weather-by-city",
    ),
    path(
        "favorites/",
        FavoriteCityListCreateView.as_view(),
        name="favorite-city-list-create",
    ),
    path(
        "favorites/<int:pk>/",
        FavoriteCityDetailView.as_view(),
        name="favorite-city-detail",
    ),
]