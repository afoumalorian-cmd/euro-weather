import {
  MapPin,
  RefreshCw,
  Trash2,
} from "lucide-react";

/**
 * Display the authenticated user's favorite cities.
 */
function FavoriteCities({
  favorites,
  loading,
  deletingId,
  onSelect,
  onDelete,
}) {
  return (
    <section className="favorite-cities-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">
            Saved locations
          </p>

          <h2>
            Favorite cities
          </h2>
        </div>

        <span className="favorite-count">
          {favorites.length}
        </span>
      </div>

      {loading ? (
        <div className="favorites-empty-state">
          <RefreshCw
            className="loading-spinner"
            size={20}
          />

          Loading favorite cities...
        </div>
      ) : favorites.length === 0 ? (
        <div className="favorites-empty-state">
          <MapPin size={22} />

          <div>
            <strong>No favorite cities yet</strong>

            <span>
              Add the currently displayed city using the heart button.
            </span>
          </div>
        </div>
      ) : (
        <div className="favorite-cities-list">
          {favorites.map((favorite) => (
            <article
              className="favorite-city-item"
              key={favorite.id}
            >
              <button
                className="favorite-city-select"
                type="button"
                onClick={() => onSelect(favorite)}
              >
                <MapPin size={18} />

                <span>
                  <strong>{favorite.city}</strong>
                  <small>{favorite.country}</small>
                </span>
              </button>

              <button
                className="favorite-city-delete"
                type="button"
                aria-label={`Remove ${favorite.city} from favorites`}
                disabled={deletingId === favorite.id}
                onClick={() => onDelete(favorite)}
              >
                {deletingId === favorite.id ? (
                  <RefreshCw
                    className="loading-spinner"
                    size={17}
                  />
                ) : (
                  <Trash2 size={17} />
                )}
              </button>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default FavoriteCities;