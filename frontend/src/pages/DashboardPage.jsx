import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Bell,
  CalendarDays,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  CloudRain,
  CloudSun,
  Gauge,
  History,
  LocateFixed,
  LogOut,
  MapPin,
  Moon,
  Navigation,
  RefreshCw,
  Search,
  Sparkles,
  Sun,
  Sunrise,
  Sunset,
  Wind,
  Heart,
  HeartOff,
  Trash2
} from "lucide-react";

import {
  getCurrentWeather,
  getDailyForecastByCity,
  getHourlyForecastByCity,
} from "../api/weatherApi";

import {
  createFavoriteCity,
  deleteFavoriteCity,
  getFavoriteCities,
} from "../api/favoritesApi";

import { getWeatherPresentation } from "../utils/weatherCode";
import { clearAuthentication } from "../api/tokenStorage";

/**
 * Return today's date in YYYY-MM-DD format using local time.
 */
function getTodayDate() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

/**
 * Format an ISO date or datetime using the browser locale.
 */
function formatDate(
  value,
  options = {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  },
) {
  if (!value) {
    return "Date unavailable";
  }

  const parsedDate = new Date(value);

  if (Number.isNaN(parsedDate.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-GB", options).format(parsedDate);
}

/**
 * Format an Open-Meteo datetime as HH:mm.
 */
function formatTime(value) {
  if (!value) {
    return "--:--";
  }

  const timePart = value.split("T")[1];

  if (!timePart) {
    return value;
  }

  return timePart.slice(0, 5);
}

/**
 * Convert degrees into a readable compass direction.
 */
function getWindDirection(degrees) {
  if (degrees === null || degrees === undefined) {
    return "Direction unavailable";
  }

  const directions = [
    "North",
    "Northeast",
    "East",
    "Southeast",
    "South",
    "Southwest",
    "West",
    "Northwest",
  ];

  const index = Math.round(Number(degrees) / 45) % directions.length;

  return directions[index];
}
/**
 * Return a greeting adapted to the current local hour.
 */
function getGreeting() {
  const currentHour = new Date().getHours();

  if (currentHour < 12) {
    return "Good morning";
  }

  if (currentHour < 18) {
    return "Good afternoon";
  }

  return "Good evening";
}

/**
 * Return the initials used by the profile avatar.
 */
function getInitials(username) {
  if (!username) {
    return "U";
  }

  return username
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join("");
}


function DashboardPage() {
  const navigate = useNavigate();
  const hourlyCarouselRef = useRef(null);
  const hourlySectionRef = useRef(null);
  const [favoritesMenuOpen, setFavoritesMenuOpen] = useState(false);

  /**
   * Scroll the hourly forecast carousel in either direction.
   */
  function scrollHourlyForecast(direction) {
    const carousel = hourlyCarouselRef.current;

    if (!carousel) {
      return;
    }

    const scrollDistance = Math.max(
      carousel.clientWidth * 0.75,
      420,
    );

    carousel.scrollBy({
      left:
        direction === "next"
          ? scrollDistance
          : -scrollDistance,
      behavior: "smooth",
    });
  }

  const username =
    localStorage.getItem("username")?.trim() || "Weather explorer";

  const greeting = getGreeting();
  const userInitials = getInitials(username);

  const [city, setCity] = useState("Paris");
  const [country, setCountry] = useState("France");
  const [selectedDate, setSelectedDate] = useState(getTodayDate());

  const [location, setLocation] = useState(null);
  const [currentWeather, setCurrentWeather] = useState(null);
  const [currentUnits, setCurrentUnits] = useState({});
  const [dailyForecast, setDailyForecast] = useState([]);
  const [dailyUnits, setDailyUnits] = useState({});
  const [hourlyForecast, setHourlyForecast] = useState([]);
  const [hourlyUnits, setHourlyUnits] = useState({});

  const [loading, setLoading] = useState(true);
  const [hourlyLoading, setHourlyLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastUpdatedAt, setLastUpdatedAt] = useState(null);

  const [favorites, setFavorites] = useState([]);
  const [favoritesLoading, setFavoritesLoading] = useState(true);
  const [favoriteSaving, setFavoriteSaving] = useState(false);
  const [deletingFavoriteId, setDeletingFavoriteId] = useState(null);
  const [favoriteError, setFavoriteError] = useState("");

  const currentPresentation = useMemo(() => {
    if (!currentWeather) {
      return {
        label: "Weather unavailable",
        icon: "🌡️",
      };
    }

    return getWeatherPresentation(
      currentWeather.weather_code,
      currentWeather.is_day,
    );
  }, [currentWeather]);

  const todayForecast = dailyForecast[0] ?? null;

  const currentFavorite = useMemo(() => {
    if (!location) {
      return null;
    }

    return favorites.find(
      (favorite) =>
        favorite.city.toLowerCase() ===
          location.name?.toLowerCase() &&
        favorite.country.toLowerCase() ===
          location.country?.toLowerCase(),
    ) ?? null;
  }, [favorites, location]);


  /**
   * Load daily, current, and hourly weather for one location.
   */
  async function loadWeather({
    requestedCity,
    requestedCountry,
    forecastDate,
  }) {
    setLoading(true);
    setError("");

    try {
      /*
       * The daily endpoint also resolves the city into geographic
       * coordinates, so it must be called first.
       */
      const dailyResponse = await getDailyForecastByCity({
        city: requestedCity,
        country: requestedCountry,
        days: 7,
      });

      const resolvedLocation = dailyResponse.location;
      const dailyData = dailyResponse.data;

      if (
        !resolvedLocation?.latitude ||
        !resolvedLocation?.longitude
      ) {
        throw new Error(
          "The selected location does not contain valid coordinates.",
        );
      }

      /*
       * Current and hourly weather can be requested in parallel
       * after the coordinates have been resolved.
       */
      const [currentResponse, hourlyResponse] = await Promise.all([
        getCurrentWeather({
          latitude: resolvedLocation.latitude,
          longitude: resolvedLocation.longitude,
        }),
        getHourlyForecastByCity({
          city: requestedCity,
          country: requestedCountry,
          forecastDate,
        }),
      ]);

      setLocation(resolvedLocation);

      setCurrentWeather(currentResponse.data?.current ?? null);
      setCurrentUnits(currentResponse.data?.units ?? {});

      setDailyForecast(dailyData?.daily ?? []);
      setDailyUnits(dailyData?.units ?? {});

      setHourlyForecast(hourlyResponse.data?.hourly ?? []);
      setHourlyUnits(hourlyResponse.data?.units ?? {});

      setLastUpdatedAt(new Date());
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The weather data could not be loaded.",
      );
    } finally {
      setLoading(false);
    }
  }

  /**
   * Add or remove the currently displayed city from favorites.
   */
  async function handleFavoriteToggle() {
    if (!location) {
      return;
    }

    setFavoriteSaving(true);
    setFavoriteError("");

    try {
      if (currentFavorite) {
        await deleteFavoriteCity(currentFavorite.id);

        setFavorites((currentFavorites) =>
          currentFavorites.filter(
            (favorite) =>
              favorite.id !== currentFavorite.id,
          ),
        );

        return;
      }

      const createdFavorite = await createFavoriteCity({
        city: location.name,
        country: location.country,
        latitude: location.latitude,
        longitude: location.longitude,
      });

      setFavorites((currentFavorites) => [
        ...currentFavorites,
        createdFavorite,
      ]);
    } catch (requestError) {
      setFavoriteError(
        requestError instanceof Error
          ? requestError.message
          : "The favorite city could not be updated.",
      );
    } finally {
      setFavoriteSaving(false);
    }
  }

  /**
  * Load weather data for a selected favorite city.
  */
  async function handleFavoriteSelect(favorite) {
    setCity(favorite.city);
    setCountry(favorite.country);

    await loadWeather({
      requestedCity: favorite.city,
      requestedCountry: favorite.country,
      forecastDate: selectedDate,
    });

    window.requestAnimationFrame(() => {
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    });
  }

  /**
   * Delete one city from the authenticated user's favorites.
   */
  async function handleFavoriteDelete(favorite) {
    setDeletingFavoriteId(favorite.id);
    setFavoriteError("");

    try {
      await deleteFavoriteCity(favorite.id);

      setFavorites((currentFavorites) =>
        currentFavorites.filter(
          (currentFavoriteItem) =>
            currentFavoriteItem.id !== favorite.id,
        ),
      );
    } catch (requestError) {
      setFavoriteError(
        requestError instanceof Error
          ? requestError.message
          : "The favorite city could not be deleted.",
      );
    } finally {
      setDeletingFavoriteId(null);
    }
  }

  /**
   * Load the authenticated user's favorite cities.
   */
  async function loadFavoriteCities() {
    setFavoritesLoading(true);
    setFavoriteError("");

    try {
      const response = await getFavoriteCities();

      setFavorites(
        Array.isArray(response)
          ? response
          : response?.results ?? [],
      );
    } catch (requestError) {
      setFavoriteError(
        requestError instanceof Error
          ? requestError.message
          : "Favorite cities could not be loaded.",
      );
    } finally {
      setFavoritesLoading(false);
    }
  }
  /**
   * Load Paris when the dashboard is opened for the first time.
   */
  useEffect(() => {
    loadWeather({
      requestedCity: "Paris",
      requestedCountry: "France",
      forecastDate: getTodayDate(),
    });

    loadFavoriteCities();
  }, []);
  
  /**
   * Submit a city and country search without reloading the page.
   */
  function handleSearch(event) {
    event.preventDefault();

    loadWeather({
      requestedCity: city.trim(),
      requestedCountry: country.trim(),
      forecastDate: selectedDate,
    });
  }

  /**
   * Reload only the hourly forecast when the selected date changes.
   */
  async function handleForecastDateChange(event) {
    const nextDate = event.target.value;

    setSelectedDate(nextDate);

    if (!nextDate || !city.trim() || !country.trim()) {
      return;
    }

    setHourlyLoading(true);
    setError("");

    try {
      const response = await getHourlyForecastByCity({
        city: city.trim(),
        country: country.trim(),
        forecastDate: nextDate,
      });

      setHourlyForecast(response.data?.hourly ?? []);
      setHourlyUnits(response.data?.units ?? {});
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The hourly forecast could not be loaded.",
      );
    } finally {
      setHourlyLoading(false);
    }
  }

  /**
 * Load the hourly forecast for a day selected
 * from the daily forecast list.
 */
async function handleDailyForecastSelect(forecastDate) {
  if (!forecastDate || !city.trim() || !country.trim()) {
    return;
  }

  setSelectedDate(forecastDate);
  setHourlyLoading(true);
  setError("");

  try {
    const response = await getHourlyForecastByCity({
      city: city.trim(),
      country: country.trim(),
      forecastDate,
    });

    setHourlyForecast(response.data?.hourly ?? []);
    setHourlyUnits(response.data?.units ?? {});

    /*
     * Move the user to the hourly forecast after
     * selecting a day from the daily list.
     */
    window.requestAnimationFrame(() => {
      hourlySectionRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });
  } catch (requestError) {
    setError(
      requestError instanceof Error
        ? requestError.message
        : "The hourly forecast could not be loaded.",
    );
  } finally {
    setHourlyLoading(false);
  }
}

  /**
   * Browser geolocation will be connected to a coordinate endpoint later.
   */
  function handleUseLocation() {
    setError(
      "Automatic geolocation will be connected in a later step.",
    );
  }

  /**
   * Clear locally stored authentication data and return to login.
   */
  function handleSignOut() {
    clearAuthentication();

    navigate("/login", {
      replace: true,
    });
  }

  return (
    <div className="weather-app">
      {/* Decorative ambient background layers. */}
      <div className="ambient-background" aria-hidden="true">
        <div className="ambient-orb ambient-orb-one" />
        <div className="ambient-orb ambient-orb-two" />
        <div className="ambient-orb ambient-orb-three" />
        <div className="ambient-grid" />
      </div>

      <header className="dashboard-header">
        <Link className="dashboard-brand" to="/dashboard">
          <span className="brand-icon">
            <Sun size={22} />
          </span>

          <span>
            Euro <strong>Weather</strong>
          </span>
        </Link>

        <nav
          className="dashboard-navigation"
          aria-label="Main navigation"
        >
          <a className="active" href="#weather">
            Weather
          </a>

          <a href="#forecast">
            Forecast
          </a>

          <Link to="/history">
            History
          </Link>
        </nav>

        <div className="header-actions">
          <button
            className="header-action-button"
            type="button"
            aria-label="Change appearance"
          >
            <Moon size={18} />
          </button>

          <button
            className="header-action-button notification-button"
            type="button"
            aria-label="Notifications"
          >
            <Bell size={18} />
            <span className="notification-dot" />
          </button>

          {/* Favorite cities menu */}
          <div className="favorites-menu-wrapper">
            <button
              className="header-action-button favorites-header-button"
              type="button"
              aria-label="Open favorite cities"
              aria-expanded={favoritesMenuOpen}
              onClick={() =>
                setFavoritesMenuOpen((isOpen) => !isOpen)
              }
            >
              <Heart size={18} />

              {favorites.length > 0 ? (
                <span className="favorites-header-count">
                  {favorites.length}
                </span>
              ) : null}
            </button>

            {favoritesMenuOpen ? (
              <div className="favorites-dropdown">
                <div className="favorites-dropdown-header">
                  <div>
                    <span>Saved locations</span>
                      <strong>Favorite cities</strong>
                  </div>

                  <span className="favorites-dropdown-count">
                    {favorites.length}
                  </span>
                </div>

                {favoritesLoading ? (
                  <div className="favorites-dropdown-empty">
                    <RefreshCw
                      className="loading-spinner"
                      size={18}
                    />

                    Loading favorites...
                  </div>
                ) : favorites.length === 0 ? (
                  <div className="favorites-dropdown-empty">
                    <Heart size={20} />

                    <div>
                      <strong>No favorite cities</strong>
                      <span>
                        Add the displayed city using the weather card.
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="favorites-dropdown-list">
                    {favorites.map((favorite) => (
                      <div
                        className="favorites-dropdown-item"
                        key={favorite.id}
                      >
                        <button
                          className="favorites-dropdown-select"
                          type="button"
                          onClick={() => {
                            handleFavoriteSelect(favorite);
                            setFavoritesMenuOpen(false);
                          }}
                        >
                          <MapPin size={17} />

                          <span>
                            <strong>{favorite.city}</strong>
                            <small>{favorite.country}</small>
                          </span>
                        </button>

                        <button
                          className="favorites-dropdown-delete"
                          type="button"
                          aria-label={`Remove ${favorite.city} from favorites`}
                          disabled={
                            deletingFavoriteId === favorite.id
                          }
                          onClick={() =>
                            handleFavoriteDelete(favorite)
                          }
                        >
                          {deletingFavoriteId === favorite.id ? (
                              <RefreshCw
                                className="loading-spinner"
                                size={16}
                            />
                          ) : (
                            <Trash2 size={16} />
                          )}
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : null}
          </div>
          
          {/* Profile */}
          <button
            className="profile-menu-button"
            type="button"
            aria-label="Open profile menu"
            onClick={() => navigate("/profile")}
          >
            <div className="profile-avatar">
              {userInitials}
            </div>
            
            
            <div className="profile-details">
              <strong>{username}</strong>
              <span>
                {location
                  ? `${location.name}, ${location.country}`
                  : "Weather explorer"}
              </span>
            </div>

            <ChevronDown size={17} />
          </button>

          <button
            className="icon-button"
            type="button"
            aria-label="Sign out"
            onClick={handleSignOut}
          >
            {/* Logout */}
            <LogOut size={18} />
          </button>
        </div>
      </header>

      <main className="dashboard-container">
        <section className="dashboard-hero">
          <div>
            <div className="hero-badge">
              <Sparkles size={14} />
              Live European weather intelligence
            </div>

            <h1>
              {greeting}, {username}.
            </h1>

            <p>
              Check current conditions, hourly changes, forecasts,
              and historical weather for cities across Europe.
            </p>

            <div className="hero-status">
              <span>
                <span className="status-dot" />
                Open-Meteo connected
              </span>

              <span>
                {lastUpdatedAt
                  ? `Updated at ${lastUpdatedAt.toLocaleTimeString(
                      [],
                      {
                        hour: "2-digit",
                        minute: "2-digit",
                      },
                    )}`
                  : "Waiting for weather data"}
              </span>
            </div>
          </div>

          <div className="hero-date">
            <CalendarDays size={20} />
            <span>{formatDate(new Date())}</span>
          </div>
        </section>

        <form
          className="weather-search"
          onSubmit={handleSearch}
        >
          <div className="search-introduction">
            <span className="search-introduction-icon">
              <Search size={18} />
            </span>

            <div>
              <strong>Explore a location</strong>
              <span>Search by city and country</span>
            </div>
          </div>

          <div className="search-field">
            <MapPin size={20} />

            <label htmlFor="city">
              <span>City</span>

              <input
                id="city"
                name="city"
                type="text"
                value={city}
                placeholder="Enter a city"
                autoComplete="address-level2"
                required
                onChange={(event) => setCity(event.target.value)}
              />
            </label>
          </div>

          <div className="search-field">
            <Navigation size={20} />

            <label htmlFor="country">
              <span>Country</span>

              <input
                id="country"
                name="country"
                type="text"
                value={country}
                placeholder="Enter a country"
                autoComplete="country-name"
                required
                onChange={(event) => setCountry(event.target.value)}
              />
            </label>
          </div>

          <button
            className="location-button"
            type="button"
            onClick={handleUseLocation}
          >
            <LocateFixed size={19} />
            Use my location
          </button>

          <button
            className="search-button"
            type="submit"
            disabled={loading}
          >
            {loading ? (
              <>
                <RefreshCw
                  className="loading-spinner"
                  size={19}
                />
                Loading
              </>
            ) : (
              <>
                <Search size={19} />
                Search weather
              </>
            )}
          </button>
        </form>

        {error ? (
          <div className="dashboard-error" role="alert">
            <strong>Unable to load weather data</strong>
            <span>{error}</span>
          </div>
        ) : null}

        {favoriteError ? (
          <div className="dashboard-error" role="alert">
            <strong>Unable to update favorites</strong>
            <span>{favoriteError}</span>
          </div>
        ) : null}

        <section
          className={`dashboard-grid ${
            loading ? "weather-content-loading" : ""
          }`}
          id="weather"
        >
          <article className="current-weather-card">
            <div className="current-weather-top">
              <div>
                <div className="location-label">
                  <MapPin size={18} />

                  {location
                    ? `${location.name}, ${location.country}`
                    : "Loading location..."}
                </div>

                <p>
                  {currentWeather?.time
                    ? `${formatDate(
                        currentWeather.time,
                        {
                          weekday: "long",
                          day: "numeric",
                          month: "long",
                        },
                      )} · ${formatTime(currentWeather.time)}`
                    : "Current conditions"}
                </p>
              </div>

              <div className="current-weather-actions">
                <span className="live-badge">
                  Live
                </span>

                <button
                  className={`favorite-toggle-button ${
                    currentFavorite
                      ? "favorite-toggle-button-active"
                      : ""
                  }`}
                  type="button"
                  disabled={!location || favoriteSaving}
                  aria-label={
                    currentFavorite
                      ? "Remove this city from favorites"
                      : "Add this city to favorites"
                  }
                  onClick={handleFavoriteToggle}
                >
                  {favoriteSaving ? (
                    <RefreshCw
                      className="loading-spinner"
                      size={18}
                    />
                  ) : currentFavorite ? (
                    <HeartOff size={18} />
                  ) : (
                    <Heart size={18} />
                  )}

                  <span>
                    {currentFavorite
                      ? "Saved"
                      : "Add favorite"}
                  </span>
                </button>
              </div>
            </div>

            <div className="current-weather-main">
              <div className="weather-condition">
                <div className="weather-symbol">
                  {currentPresentation.icon}
                </div>

                <div>
                  <strong>{currentPresentation.label}</strong>

                  <span>
                    Feels like{" "}
                    {currentWeather?.apparent_temperature ?? "--"}
                    {currentUnits.apparent_temperature ?? "°C"}
                  </span>
                </div>
              </div>

              <div className="temperature-value">
                {currentWeather?.temperature ?? "--"}

                <span>
                  {currentUnits.temperature ?? "°C"}
                </span>
              </div>
            </div>

            <div className="sun-times">
              <div>
                <Sunrise size={20} />

                <span>
                  Sunrise
                  <strong>
                    {formatTime(todayForecast?.sunrise)}
                  </strong>
                </span>
              </div>

              <div>
                <Sunset size={20} />

                <span>
                  Sunset
                  <strong>
                    {formatTime(todayForecast?.sunset)}
                  </strong>
                </span>
              </div>
            </div>

            <div className="current-weather-summary">
              <div>
                <span>High</span>
                <strong>
                  {todayForecast?.temperature_max ?? "--"}
                  {dailyUnits.temperature_max ?? "°C"}
                </strong>
              </div>

              <div>
                <span>Low</span>
                <strong>
                  {todayForecast?.temperature_min ?? "--"}
                  {dailyUnits.temperature_min ?? "°C"}
                </strong>
              </div>

              <div>
                <span>Cloud cover</span>
                <strong>
                  {currentWeather?.cloud_cover ?? "--"}
                  {currentUnits.cloud_cover ?? "%"}
                </strong>
              </div>

              <div>
                <span>Wind gusts</span>
                <strong>
                  {currentWeather?.wind_gusts ?? "--"}{" "}
                  {currentUnits.wind_gusts ?? "km/h"}
                </strong>
              </div>
            </div>
          </article>

          <div className="weather-metrics">
            <article className="metric-box">
              <div className="metric-icon">
                <CloudRain size={21} />
              </div>

              <span>Precipitation</span>

              <strong>
                {currentWeather?.precipitation ?? "--"}{" "}
                {currentUnits.precipitation ?? "mm"}
              </strong>

              <small>
                Current amount
              </small>
            </article>

            <article className="metric-box">
              <div className="metric-icon">
                <Wind size={21} />
              </div>

              <span>Wind</span>

              <strong>
                {currentWeather?.wind_speed ?? "--"}{" "}
                {currentUnits.wind_speed ?? "km/h"}
              </strong>

              <small>
                {getWindDirection(
                  currentWeather?.wind_direction,
                )}
              </small>
            </article>

            <article className="metric-box">
              <div className="metric-icon">
                <Gauge size={21} />
              </div>

              <span>Humidity</span>

              <strong>
                {currentWeather?.relative_humidity ?? "--"}
                {currentUnits.relative_humidity ?? "%"}
              </strong>

              <small>
                Relative humidity
              </small>
            </article>

            <article className="metric-box">
              <div className="metric-icon">
                <CloudSun size={21} />
              </div>

              <span>Cloud cover</span>

              <strong>
                {currentWeather?.cloud_cover ?? "--"}
                {currentUnits.cloud_cover ?? "%"}
              </strong>

              <small>
                Current sky coverage
              </small>
            </article>
          </div>
        </section>

        <section
          className="forecast-grid"
          id="forecast"
        >
          <article
            className="forecast-panel hourly-panel"
            ref={hourlySectionRef}
          >
            <div className="panel-header hourly-panel-header">
              <div>
                <p className="eyebrow">
                  Selected date
                </p>

                <h2>
                  Hourly forecast
                </h2>
              </div>

              <div className="hourly-panel-actions">
                <input
                  className="forecast-date"
                  type="date"
                  value={selectedDate}
                  min={getTodayDate()}
                  aria-label="Select hourly forecast date"
                  onChange={handleForecastDateChange}
                />

                <div
                  className="carousel-controls"
                  aria-label="Hourly forecast navigation"
                >
                  <button
                    type="button"
                    aria-label="Show previous hours"
                    onClick={() => scrollHourlyForecast("previous")}
                  >
                    <ChevronLeft size={18} />
                  </button>

                  <button
                    type="button"
                    aria-label="Show next hours"
                    onClick={() => scrollHourlyForecast("next")}
                  >
                    <ChevronRight size={18} />
                  </button>
                </div>
              </div>
            </div>

            {hourlyLoading ? (
              <div className="forecast-loading">
                <RefreshCw
                  className="loading-spinner"
                  size={22}
                />
                Loading hourly forecast...
              </div>
            ) : hourlyForecast.length === 0 ? (
              <div className="forecast-loading">
                No hourly forecast is available for this date.
              </div>
            ) : (
              <div className="hourly-carousel-shell">
                <div
                  className="hourly-carousel"
                  ref={hourlyCarouselRef}
                >
                  {hourlyForecast.map((forecast, index) => {
                    const presentation = getWeatherPresentation(
                      forecast.weather_code,
                      forecast.is_day,
                    );

                    return (
                      <article
                        className={`hourly-slide ${
                          index === 0
                            ? "hourly-slide-active"
                            : ""
                        }`}
                        key={forecast.time}
                      >
                        <span className="hourly-slide-time">
                          {formatTime(forecast.time)}
                        </span>

                        <strong className="hourly-slide-icon">
                          {presentation.icon}
                        </strong>

                        <strong className="hourly-slide-temperature">
                          {forecast.temperature ?? "--"}
                          {hourlyUnits.temperature ?? "°C"}
                        </strong>

                        <span className="hourly-slide-condition">
                          {presentation.label}
                        </span>

                        <div className="hourly-slide-details">
                          <span>
                            <CloudRain size={14} />

                            {forecast.precipitation_probability ?? 0}
                            {hourlyUnits.precipitation_probability ?? "%"}
                          </span>

                          <span>
                            <Wind size={14} />

                            {forecast.wind_speed ?? "--"}{" "}
                            {hourlyUnits.wind_speed ?? "km/h"}
                          </span>
                        </div>
                      </article>
                    );
                  })} 
                </div>
              </div>
            )}
          </article>

          <article className="forecast-panel daily-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">
                  Next days
                </p>

                <h2>
                  Daily forecast
                </h2>
              </div>

              <button
                className="text-button"
                type="button"
              >
                View all
              </button>
            </div>

            <div className="daily-list">
              {dailyForecast.slice(0, 7).map((forecast) => {
                const presentation = getWeatherPresentation(
                  forecast.weather_code,
                  true
                );

                return (
                  <button
                    className={`daily-item daily-item-button ${
                      selectedDate === forecast.date
                        ? "daily-item-selected"
                        : ""
                    }`}
                    key={forecast.date}
                    type="button"
                    onClick={() => handleDailyForecastSelect(forecast.date)}
                  >
                    <span className="daily-icon">
                      {presentation.icon}
                    </span>

                    <div>
                      <strong>
                        {formatDate(forecast.date, {
                          weekday: "long",
                        })}
                      </strong>

                      <span>
                        {presentation.label}
                      </span>
                    </div>

                    <p>
                      <span>
                        {forecast.temperature_min ?? "--"}°
                      </span>

                      <strong>
                        {forecast.temperature_max ?? "--"}°
                      </strong>
                    </p>
                  </button>
                );
              })}
            </div>
          </article>
        </section>

        <section
          className="history-banner"
          id="history"
        >
          <div className="history-icon">
            <History size={26} />
          </div>

          <div>
            <p className="eyebrow">
              Weather archive
            </p>

            <h2>
              Explore historical weather
            </h2>

            <p>
              Compare temperatures, rainfall, and wind conditions
              from previous dates.
            </p>
          </div>

          <Link 
            className="history-banner-button"
            to="/history"
          >
            Open history
          </Link>
        </section>
      </main>
    </div>
  );
}

export default DashboardPage;