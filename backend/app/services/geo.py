"""India-focused geocoding with provider fallback and OSM routing.

Photon is used for interactive suggestions because Nominatim explicitly
prohibits client-side autocomplete. Explicit searches may fall back to
Nominatim, respecting its one-request-per-second application-wide limit.
Both public community endpoints are best-effort services, not an SLA.
"""
import asyncio
import time
from typing import Any

import httpx

PHOTON_URL = "https://photon.komoot.io/api/"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
VALHALLA_URL = "https://valhalla1.openstreetmap.de/route"
OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
VALHALLA_COSTING = {
    "driving": "auto",
    "motorcycle": "motorcycle",  # Valhalla marks this profile as beta.
    "scooter": "motor_scooter",
    "cycling": "bicycle",
    "walking": "pedestrian",
}
HEADERS = {
    "User-Agent": "LocalLensAI/0.3 (https://locallens-ai-frontend.onrender.com; India place and commute search)",
    "X-Client-Id": "locallens-ai-frontend.onrender.com",
    "Accept": "application/json",
}
_CACHE_TTL_SECONDS = 60 * 60 * 24
_search_cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}
_nominatim_lock = asyncio.Lock()
_last_nominatim_request = 0.0


def _cache_get(key: str) -> list[dict[str, Any]] | None:
    cached = _search_cache.get(key)
    if cached and time.monotonic() - cached[0] < _CACHE_TTL_SECONDS:
        return cached[1]
    if cached:
        _search_cache.pop(key, None)
    return None


def _cache_set(key: str, rows: list[dict[str, Any]]) -> None:
    # Keep the in-process cache bounded on the free single-instance service.
    if len(_search_cache) > 1000:
        oldest = min(_search_cache, key=lambda item: _search_cache[item][0])
        _search_cache.pop(oldest, None)
    _search_cache[key] = (time.monotonic(), rows)


def _normalise_photon(payload: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for feature in payload.get("features", []):
        props = feature.get("properties") or {}
        coords = (feature.get("geometry") or {}).get("coordinates") or []
        if len(coords) < 2:
            continue
        # Photon countrycode is ISO-3166-1 alpha-2. Do not leak foreign matches.
        country_code = str(props.get("countrycode") or "").lower()
        country = str(props.get("country") or "").lower()
        if country_code and country_code != "in":
            continue
        if not country_code and country and country not in {"india", "भारत"}:
            continue
        parts = [
            props.get("name"), props.get("street"), props.get("district"),
            props.get("city"), props.get("state"), props.get("country"),
        ]
        display_name = ", ".join(dict.fromkeys(str(part).strip() for part in parts if part))
        if not display_name:
            display_name = "India place"
        results.append({
            "display_name": display_name,
            "latitude": float(coords[1]),
            "longitude": float(coords[0]),
            "category": props.get("type") or props.get("osm_value"),
        })
    return results


async def _photon_search(query: str, limit: int) -> list[dict[str, Any]]:
    params = {"q": query, "limit": limit, "lang": "en", "countrycode": "in"}
    async with httpx.AsyncClient(timeout=12, headers=HEADERS) as client:
        response = await client.get(PHOTON_URL, params=params)
        response.raise_for_status()
        return _normalise_photon(response.json())


async def _nominatim_search(query: str, limit: int) -> list[dict[str, Any]]:
    global _last_nominatim_request
    params = {
        "q": query,
        "format": "jsonv2",
        "limit": limit,
        "addressdetails": 1,
        "countrycodes": "in",
    }
    # The public Nominatim policy sets a hard maximum of one request/second
    # for the whole application. The lock serialises requests on this instance.
    async with _nominatim_lock:
        wait = 1.0 - (time.monotonic() - _last_nominatim_request)
        if wait > 0:
            await asyncio.sleep(wait)
        async with httpx.AsyncClient(timeout=12, headers=HEADERS) as client:
            response = await client.get(NOMINATIM_URL, params=params)
            _last_nominatim_request = time.monotonic()
            response.raise_for_status()
            rows = response.json()
    return [
        {
            "display_name": row.get("display_name", "Unknown place"),
            "latitude": float(row["lat"]),
            "longitude": float(row["lon"]),
            "category": row.get("type"),
        }
        for row in rows
    ]


async def _open_meteo_search(query: str, limit: int) -> list[dict[str, Any]]:
    """Last-resort city/locality geocoder; this provider does not resolve street addresses."""
    # Open-Meteo accepts a place name rather than a free-form address.
    name = query.split(",")[0].strip()
    if len(name) < 2:
        return []
    params = {"name": name, "count": limit, "language": "en", "format": "json"}
    async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
        response = await client.get(OPEN_METEO_GEOCODING_URL, params=params)
        response.raise_for_status()
        payload = response.json()
    rows = []
    for item in payload.get("results") or []:
        if str(item.get("country_code") or "").upper() != "IN":
            continue
        parts = [item.get("name"), item.get("admin2"), item.get("admin1"), item.get("country")]
        display_name = ", ".join(dict.fromkeys(str(part).strip() for part in parts if part))
        rows.append({
            "display_name": display_name,
            "latitude": float(item["latitude"]),
            "longitude": float(item["longitude"]),
            "category": item.get("feature_code"),
        })
    return rows


async def suggest_places(query: str, limit: int = 6) -> list[dict]:
    """Interactive suggestions use Photon, with a city/locality fallback."""
    key = "suggest:" + query.strip().casefold()
    cached = _cache_get(key)
    if cached is not None:
        return cached
    try:
        rows = await _photon_search(query, limit)
        if rows:
            _cache_set(key, rows)
            return rows
    except (httpx.HTTPError, ValueError, KeyError, TypeError, RuntimeError):
        pass
    rows = await _open_meteo_search(query, limit)
    _cache_set(key, rows)
    return rows


async def search_places(query: str, limit: int = 8) -> list[dict]:
    """Search India via Photon, falling back to Nominatim for explicit searches."""
    key = "search:" + query.strip().casefold()
    cached = _cache_get(key)
    if cached is not None:
        return cached
    photon_error: Exception | None = None
    try:
        rows = await _photon_search(query, limit)
        if rows:
            _cache_set(key, rows)
            return rows
    except (httpx.HTTPError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        photon_error = exc
    nominatim_error: Exception | None = None
    try:
        rows = await _nominatim_search(query, limit)
        if rows:
            _cache_set(key, rows)
            return rows
    except (httpx.HTTPError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        nominatim_error = exc

    try:
        rows = await _open_meteo_search(query, limit)
        _cache_set(key, rows)
        return rows
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        if photon_error or nominatim_error:
            raise RuntimeError("All India place-search providers are unavailable.") from exc
        raise


async def estimate_route(
    origin_lon: float,
    origin_lat: float,
    destination_lon: float,
    destination_lat: float,
    mode: str,
) -> dict:
    """Request a real OSM route for an enabled vehicle, cycle or walking profile."""
    if mode not in VALHALLA_COSTING:
        raise ValueError(
            "Public transport routing is not enabled: verified Indian city "
            "transit timetable feeds are not configured yet."
        )

    request_body = {
        "locations": [
            {"lat": origin_lat, "lon": origin_lon},
            {"lat": destination_lat, "lon": destination_lon},
        ],
        "costing": VALHALLA_COSTING[mode],
        "units": "km",
        "shape_format": "polyline6",
        "directions_options": {"units": "kilometers"},
    }

    async with httpx.AsyncClient(timeout=25, headers=HEADERS) as client:
        response = await client.post(VALHALLA_URL, json=request_body)
        response.raise_for_status()
        payload = response.json()

    trip = payload.get("trip") or {}
    summary = trip.get("summary") or {}
    legs = trip.get("legs") or []
    if payload.get("error") or not summary or not legs:
        message = payload.get("error") or "No route was returned."
        raise ValueError(str(message))

    return {
        "distance_km": round(float(summary["length"]), 2),
        "duration_minutes": round(float(summary["time"]) / 60, 1),
        "mode": mode,
        "geometry": legs[0].get("shape", ""),
        "provider": "Valhalla routing on OpenStreetMap data",
        "disclaimer": (
            "Route and duration are model estimates from mapped road/path data. "
            "They do not include live traffic, real-time disruptions or guaranteed "
            "Indian public-transport timetables."
        ),
    }
