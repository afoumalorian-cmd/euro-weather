import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  createFavoriteCity,
  deleteFavoriteCity,
  getFavoriteCities,
} from "../api/favoritesApi";
import {
  apiDelete,
  apiGet,
  apiPost,
} from "../api/apiClient";

vi.mock("../api/apiClient", () => ({
  apiDelete: vi.fn(),
  apiGet: vi.fn(),
  apiPost: vi.fn(),
}));

describe("favoritesApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("retrieves the authenticated user's favorite cities", async () => {
    const expectedResponse = [
      {
        id: 1,
        city: "Paris",
        country: "France",
      },
    ];

    apiGet.mockResolvedValue(expectedResponse);

    const result = await getFavoriteCities();

    expect(apiGet).toHaveBeenCalledWith(
      "/api/weather/favorites/",
    );

    expect(result).toEqual(expectedResponse);
  });

  it("creates a favorite city with location data", async () => {
    const favoritePayload = {
      city: "Berlin",
      country: "Germany",
      latitude: 52.52,
      longitude: 13.405,
    };

    const expectedResponse = {
      id: 2,
      ...favoritePayload,
    };

    apiPost.mockResolvedValue(expectedResponse);

    const result = await createFavoriteCity(
      favoritePayload,
    );

    expect(apiPost).toHaveBeenCalledWith(
      "/api/weather/favorites/",
      favoritePayload,
    );

    expect(result).toEqual(expectedResponse);
  });

  it("deletes a favorite city using its identifier", async () => {
    apiDelete.mockResolvedValue(null);

    const result = await deleteFavoriteCity(5);

    expect(apiDelete).toHaveBeenCalledWith(
      "/api/weather/favorites/5/",
    );

    expect(result).toBeNull();
  });

  it("propagates errors returned while loading favorites", async () => {
    apiGet.mockRejectedValue(
      new Error("Favorites could not be loaded."),
    );

    await expect(
      getFavoriteCities(),
    ).rejects.toThrow(
      "Favorites could not be loaded.",
    );
  });

  it("propagates errors returned while creating a favorite", async () => {
    apiPost.mockRejectedValue(
      new Error(
        "This city is already present in your favorites.",
      ),
    );

    await expect(
      createFavoriteCity({
        city: "Paris",
        country: "France",
        latitude: 48.8566,
        longitude: 2.3522,
      }),
    ).rejects.toThrow(
      "This city is already present in your favorites.",
    );
  });

  it("propagates errors returned while deleting a favorite", async () => {
    apiDelete.mockRejectedValue(
      new Error("Favorite city could not be deleted."),
    );

    await expect(
      deleteFavoriteCity(5),
    ).rejects.toThrow(
      "Favorite city could not be deleted.",
    );
  });
});