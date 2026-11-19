"""India-focused place search and multi-profile OpenStreetMap routing.

Nominatim and the public Valhalla demo are community services. They are
appropriate for a prototype, not a high-volume production SLA.
"""
import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
VALHALLA_URL = "https://valhalla1.openstreetmap.de/route"
VALHALLA_COSTING = {
    "driving": "auto",
    "cycling": "bicycle",
    "walking": "pedestrian",
}
HEADERS = {
    "User-Agent": "LocalLensAI/0.2 (India neighbourhood research application)",
    "Accept": "application/json",
}


async def search_places(query: str, limit: int = 8) -> list[dict]:
    """Search all Indian states and union territories using OSM Nominatim."""
    params = {
        "q": query,
        "format": "jsonv2",
        "limit": limit,
        "addressdetails": 1,
        "countrycodes": "in",
    }
    async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
        response = await client.get(NOMINATIM_URL, params=params)
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


async def estimate_route(
    origin_lon: float,
    origin_lat: float,
    destination_lon: float,
    destination_lat: float,
    mode: str,
) -> dict:
    """Request a real OSM route for driving, cycling or walking.

    Public-transport itineraries need city/agency GTFS feeds. They are not
    fabricated here; the API reports the mode as unsupported instead.
    """
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
        "units": "kilometers",
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

    # Valhalla returns distance in the requested units and time in seconds.
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
