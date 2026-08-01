import {
  ArrowLeft,
  CalendarDays,
  CloudRain,
  Gauge,
  History,
  MapPin,
  RefreshCw,
  Search,
  Thermometer,
  Wind,
} from "lucide-react";
import {
  useMemo,
  useState,
} from "react";
import {
  Link,
  useNavigate,
} from "react-router-dom";

import { getHistoricalWeatherByCity } from "../api/weatherApi";
import { clearAuthentication } from "../api/tokenStorage";
import { getWeatherPresentation } from "../utils/weatherCode";

/**
 * Return a date formatted as YYYY-MM-DD.
 */
function formatDateForInput(date) {
  const year = date.getFullYear();
  const month = String(
    date.getMonth() + 1,
  ).padStart(2, "0");
  const day = String(
    date.getDate(),
  ).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

/**
 * Return a default historical start date.
 */
function getDefaultStartDate() {
  const date = new Date();

  date.setDate(date.getDate() - 7);

  return formatDateForInput(date);
}

/**
 * Return a default historical end date.
 */
function getDefaultEndDate() {
  const date = new Date();

  date.setDate(date.getDate() - 1);

  return formatDateForInput(date);
}

/**
 * Format an ISO date using the browser locale.
 */
function formatDisplayDate(value) {
  if (!value) {
    return "Date unavailable";
  }

  const parsedDate = new Date(`${value}T00:00:00`);

  if (Number.isNaN(parsedDate.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-GB", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(parsedDate);
}

/**
 * Return a numeric average or null when no valid value exists.
 */
function calculateAverage(values) {
  const validValues = values
    .map(Number)
    .filter((value) => Number.isFinite(value));

  if (validValues.length === 0) {
    return null;
  }

  const total = validValues.reduce(
    (sum, value) => sum + value,
    0,
  );

  return total / validValues.length;
}

/**
 * Return a readable metric value.
 */
function formatMetric(value, unit = "") {
  const numericValue = Number(value);

  if (!Number.isFinite(numericValue)) {
    return "--";
  }

  return `${numericValue.toFixed(1)}${unit}`;
}

function WeatherHistoryPage() {
  const navigate = useNavigate();

  const [city, setCity] = useState("Paris");
  const [country, setCountry] = useState("France");
  const [startDate, setStartDate] = useState(
    getDefaultStartDate(),
  );
  const [endDate, setEndDate] = useState(
    getDefaultEndDate(),
  );

  const [location, setLocation] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [units, setUnits] = useState({});

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);

  const summary = useMemo(() => {
    if (historicalData.length === 0) {
      return {
        averageMaximum: null,
        averageMinimum: null,
        totalPrecipitation: null,
        averageWindSpeed: null,
      };
    }

    const averageMaximum = calculateAverage(
      historicalData.map(
        (day) => day.temperature_max,
      ),
    );

    const averageMinimum = calculateAverage(
      historicalData.map(
        (day) => day.temperature_min,
      ),
    );

    const precipitationValues = historicalData
      .map((day) => Number(day.precipitation_sum))
      .filter((value) => Number.isFinite(value));

    const totalPrecipitation =
      precipitationValues.length > 0
        ? precipitationValues.reduce(
            (sum, value) => sum + value,
            0,
          )
        : null;

    const averageWindSpeed = calculateAverage(
      historicalData.map(
        (day) => day.wind_speed_max,
      ),
    );

    return {
      averageMaximum,
      averageMinimum,
      totalPrecipitation,
      averageWindSpeed,
    };
  }, [historicalData]);

  /**
   * Request historical weather data for the selected location and dates.
   */
  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setHasSearched(true);

    if (startDate > endDate) {
      setError(
        "The start date must be earlier than or equal to the end date.",
      );

      return;
    }

    setLoading(true);

    try {
      const response = await getHistoricalWeatherByCity({
        city: city.trim(),
        country: country.trim(),
        startDate,
        endDate,
      });

      setLocation(response.location ?? null);
      setHistoricalData(
        response.data?.daily ?? [],
      );
      setUnits(
        response.data?.units ?? {},
      );
    } catch (requestError) {
      setLocation(null);
      setHistoricalData([]);
      setUnits({});

      setError(
        requestError instanceof Error
          ? requestError.message
          : "Historical weather could not be loaded.",
      );
    } finally {
      setLoading(false);
    }
  }

  /**
   * Clear authentication data and return to the login page.
   */
  function handleSignOut() {
    clearAuthentication();

    navigate("/login", {
      replace: true,
    });
  }

  return (
    <div className="weather-history-page">
      <header className="history-page-header">
        <Link
          className="dashboard-brand"
          to="/dashboard"
        >
          <span className="brand-icon">
            <History size={21} />
          </span>

          <span>
            Euro <strong>Weather</strong>
          </span>
        </Link>

        <nav
          className="dashboard-navigation"
          aria-label="Main navigation"
        >
          <Link to="/dashboard">
            Weather
          </Link>

          <Link to="/dashboard#forecast">
            Forecast
          </Link>

          <Link
            className="active"
            to="/history"
          >
            History
          </Link>
        </nav>

        <button
          className="history-sign-out-button"
          type="button"
          onClick={handleSignOut}
        >
          Sign out
        </button>
      </header>

      <main className="history-page-container">
        <section className="history-page-hero">
          <div>
            <Link
              className="history-back-link"
              to="/dashboard"
            >
              <ArrowLeft size={17} />
              Back to dashboard
            </Link>

            <div className="hero-badge">
              <History size={14} />
              European weather archive
            </div>

            <h1>
              Explore historical weather
            </h1>

            <p>
              Search past temperatures, rainfall, weather conditions,
              and wind data for cities across Europe.
            </p>
          </div>
        </section>

        <form
          className="history-search-form"
          onSubmit={handleSubmit}
        >
          <div className="history-search-field">
            <MapPin size={19} />

            <label htmlFor="history-city">
              <span>City</span>

              <input
                id="history-city"
                type="text"
                value={city}
                required
                placeholder="Enter a city"
                onChange={(event) =>
                  setCity(event.target.value)
                }
              />
            </label>
          </div>

          <div className="history-search-field">
            <MapPin size={19} />

            <label htmlFor="history-country">
              <span>Country</span>

              <input
                id="history-country"
                type="text"
                value={country}
                required
                placeholder="Enter a country"
                onChange={(event) =>
                  setCountry(event.target.value)
                }
              />
            </label>
          </div>

          <div className="history-search-field">
            <CalendarDays size={19} />

            <label htmlFor="history-start-date">
              <span>Start date</span>

              <input
                id="history-start-date"
                type="date"
                value={startDate}
                required
                max={endDate}
                onChange={(event) =>
                  setStartDate(event.target.value)
                }
              />
            </label>
          </div>

          <div className="history-search-field">
            <CalendarDays size={19} />

            <label htmlFor="history-end-date">
              <span>End date</span>

              <input
                id="history-end-date"
                type="date"
                value={endDate}
                required
                min={startDate}
                max={getDefaultEndDate()}
                onChange={(event) =>
                  setEndDate(event.target.value)
                }
              />
            </label>
          </div>

          <button
            className="history-search-button"
            type="submit"
            disabled={loading}
          >
            {loading ? (
              <>
                <RefreshCw
                  className="loading-spinner"
                  size={18}
                />
                Loading
              </>
            ) : (
              <>
                <Search size={18} />
                Search history
              </>
            )}
          </button>
        </form>

        {error ? (
          <div
            className="dashboard-error"
            role="alert"
          >
            <strong>
              Unable to load historical weather
            </strong>

            <span>{error}</span>
          </div>
        ) : null}

        {loading ? (
          <section className="history-loading-state">
            <RefreshCw
              className="loading-spinner"
              size={28}
            />

            <div>
              <strong>
                Loading historical weather
              </strong>

              <span>
                Retrieving archive data for the selected location.
              </span>
            </div>
          </section>
        ) : null}

        {!loading &&
        hasSearched &&
        historicalData.length === 0 &&
        !error ? (
          <section className="history-empty-state">
            <History size={30} />

            <div>
              <strong>
                No historical records found
              </strong>

              <span>
                Try another city or select a different date range.
              </span>
            </div>
          </section>
        ) : null}

        {!loading && historicalData.length > 0 ? (
          <>
            <section className="history-results-heading">
              <div>
                <p className="eyebrow">
                  Historical results
                </p>

                <h2>
                  {location
                    ? `${location.name}, ${location.country}`
                    : `${city}, ${country}`}
                </h2>

                <span>
                  {formatDisplayDate(startDate)}
                  {" — "}
                  {formatDisplayDate(endDate)}
                </span>
              </div>

              <span className="history-result-count">
                {historicalData.length} days
              </span>
            </section>

            <section className="history-summary-grid">
              <article className="history-summary-card">
                <div className="metric-icon">
                  <Thermometer size={21} />
                </div>

                <span>
                  Average high
                </span>

                <strong>
                  {formatMetric(
                    summary.averageMaximum,
                    units.temperature_max ?? "°C",
                  )}
                </strong>
              </article>

              <article className="history-summary-card">
                <div className="metric-icon">
                  <Gauge size={21} />
                </div>

                <span>
                  Average low
                </span>

                <strong>
                  {formatMetric(
                    summary.averageMinimum,
                    units.temperature_min ?? "°C",
                  )}
                </strong>
              </article>

              <article className="history-summary-card">
                <div className="metric-icon">
                  <CloudRain size={21} />
                </div>

                <span>
                  Total rainfall
                </span>

                <strong>
                  {formatMetric(
                    summary.totalPrecipitation,
                    units.precipitation_sum ?? "mm",
                  )}
                </strong>
              </article>

              <article className="history-summary-card">
                <div className="metric-icon">
                  <Wind size={21} />
                </div>

                <span>
                  Average max wind
                </span>

                <strong>
                  {formatMetric(
                    summary.averageWindSpeed,
                    units.wind_speed_max ?? "km/h",
                  )}
                </strong>
              </article>
            </section>

            <section className="history-table-panel">
              <div className="panel-header">
                <div>
                  <p className="eyebrow">
                    Daily archive
                  </p>

                  <h2>
                    Weather by day
                  </h2>
                </div>
              </div>

              <div className="history-table-wrapper">
                <table className="history-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Condition</th>
                      <th>Minimum</th>
                      <th>Maximum</th>
                      <th>Rainfall</th>
                      <th>Max wind</th>
                    </tr>
                  </thead>

                  <tbody>
                    {historicalData.map((day) => {
                      const presentation =
                        getWeatherPresentation(
                          day.weather_code,
                          true,
                        );

                      return (
                        <tr key={day.date}>
                          <td>
                            {formatDisplayDate(
                              day.date,
                            )}
                          </td>

                          <td>
                            <span className="history-condition">
                              <span>
                                {presentation.icon}
                              </span>

                              {presentation.label}
                            </span>
                          </td>

                          <td>
                            {day.temperature_min ?? "--"}
                            {units.temperature_min ?? "°C"}
                          </td>

                          <td>
                            <strong>
                              {day.temperature_max ?? "--"}
                              {units.temperature_max ?? "°C"}
                            </strong>
                          </td>

                          <td>
                            {day.precipitation_sum ?? "--"}{" "}
                            {units.precipitation_sum ?? "mm"}
                          </td>

                          <td>
                            {day.wind_speed_max ?? "--"}{" "}
                            {units.wind_speed_max ?? "km/h"}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        ) : null}
      </main>
    </div>
  );
}

export default WeatherHistoryPage;