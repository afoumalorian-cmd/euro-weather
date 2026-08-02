import hashlib
import json
from typing import Any


CURRENT_WEATHER_CACHE_TIMEOUT = 5 * 60
HOURLY_FORECAST_CACHE_TIMEOUT = 15 * 60
DAILY_FORECAST_CACHE_TIMEOUT = 30 * 60
HISTORICAL_WEATHER_CACHE_TIMEOUT = 24 * 60 * 60
LOCATION_SEARCH_CACHE_TIMEOUT = 24 * 60 * 60
REVERSE_GEOCODING_CACHE_TIMEOUT = 24 * 60 * 60


def build_cache_key(prefix: str, **parameters: Any) -> str:
    """
    Build a stable cache key from a prefix and request parameters.

    Parameters are sorted and serialized before hashing so that their order
    does not affect the generated cache key.
    """
    normalized_parameters = {
        key: _normalize_value(value)
        for key, value in sorted(parameters.items())
        if value is not None
    }

    serialized_parameters = json.dumps(
        normalized_parameters,
        sort_keys=True,
        separators=(",", ":"),
    )

    parameters_hash = hashlib.sha256(
        serialized_parameters.encode("utf-8")
    ).hexdigest()[:16]

    return f"weather:{prefix}:{parameters_hash}"


def _normalize_value(value: Any) -> Any:
    """
    Normalize a value before including it in a cache key.
    """
    if isinstance(value, float):
        return round(value, 4)

    if isinstance(value, str):
        return value.strip().lower()

    if isinstance(value, (list, tuple)):
        return [_normalize_value(item) for item in value]

    if isinstance(value, dict):
        return {
            key: _normalize_value(item)
            for key, item in sorted(value.items())
        }

    return value