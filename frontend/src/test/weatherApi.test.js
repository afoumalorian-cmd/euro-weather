import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  getCurrentWeather,
  getDailyForecastByCity,
  getHistoricalWeatherByCity,
  getHourlyForecastByCity,
} from "../api/weatherApi";
import { apiGet } from "../api/apiClient";

vi.mock("../api/apiClient", () => ({
  apiGet: vi.fn(),
}));

describe("weatherApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("requests the current weather with coordinates", async () => {
    const expectedResponse = {
      success: true,
      data: {
        current: {
          temperature: 21,
        },
      },
    };

    apiGet.mockResolvedValue(expectedResponse);

    const result = await getCurrentWeather({
      latitude: 48.8566,
      longitude: 2.3522,
    });

    expect(apiGet).toHaveBeenCalledWith(
      "/api/weather/current/",
      {
        latitude: 48.8566,
        longitude: 2.3522,
      },
    );

    expect(result).toEqual(expectedResponse);
  });

  it("requests the daily forecast by city and country", async () => {
    apiGet.mockResolvedValue({
      success: true,
    });

    await getDailyForecastByCity({
      city: "Paris",
      country: "France",
      days: 7,
    });

    expect(apiGet).toHaveBeenCalledWith(
      "/api/weather/forecast/daily/by-city/",
      {
        city: "Paris",
        country: "France",
        days: 7,
      },
    );
  });

  it("uses seven days by default for the daily forecast", async () => {
    apiGet.mockResolvedValue({
      success: true,
    });

    await getDailyForecastByCity({
      city: "Berlin",
      country: "Germany",
    });

    expect(apiGet).toHaveBeenCalledWith(
      "/api/weather/forecast/daily/by-city/",
      {
        city: "Berlin",
        country: "Germany",
        days: 7,
      },
    );
  });

  it("requests the hourly forecast using forecast_date", async () => {
    apiGet.mockResolvedValue({
      success: true,
    });

    await getHourlyForecastByCity({
      city: "Madrid",
      country: "Spain",
      forecastDate: "2026-08-01",
    });

    expect(apiGet).toHaveBeenCalledWith(
      "/api/weather/forecast/hourly/by-city/",
      {
        city: "Madrid",
        country: "Spain",
        forecast_date: "2026-08-01",
      },
    );
  });

  it("requests historical weather using the selected date range", async () => {
    apiGet.mockResolvedValue({
      success: true,
    });

    await getHistoricalWeatherByCity({
      city: "Rome",
      country: "Italy",
      startDate: "2026-07-01",
      endDate: "2026-07-07",
    });

    expect(apiGet).toHaveBeenCalledWith(
      "/api/weather/history/by-city/",
      {
        city: "Rome",
        country: "Italy",
        start_date: "2026-07-01",
        end_date: "2026-07-07",
      },
    );
  });

  it("propagates errors returned by apiGet", async () => {
    apiGet.mockRejectedValue(
      new Error("Weather service unavailable."),
    );

    await expect(
      getCurrentWeather({
        latitude: 48.8566,
        longitude: 2.3522,
      }),
    ).rejects.toThrow(
      "Weather service unavailable.",
    );
  });
});