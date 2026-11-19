"""OpenStreetMap geocoding and OSRM route adapters.

Public community endpoints are rate-limited and are not an SLA-backed service.
For production traffic, configure contracted providers and follow their policies.
"""
import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_PROFILES = {"driving": "driving", "cycling": "cycling", "walking": "foot"}
HEADERS = {"User-Agent": "LocalLensAI/0.1 (neighbourhood research application)"}


async def search_places(query: str, limit: int = 6) -> list[dict]:
    params = {"q": query, "format": "jsonv2", "limit": limit, "addressdetails": 0}
    async with httpx.AsyncClient(timeout=12, headers=HEADERS) as client:
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


async def estimate_route(origin_lon: float, origin_lat: float, destination_lon: float,
                         destination_lat: float, mode: str) -> dict:
    profile = OSRM_PROFILES[mode]
    url = (
        f"https://router.project-osrm.org/route/v1/{profile}/"
        f"{origin_lon},{origin_lat};{destination_lon},{destination_lat}"
    )
    async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
        response = await client.get(url, params={"overview": "false", "alternatives": "false"})
        response.raise_for_status()
        payload = response.json()
    if payload.get("code") != "Ok" or not payload.get("routes"):
        raise ValueError("No route could be found for these locations and travel mode.")
    route = payload["routes"][0]
    return {
        "distance_km": round(route["distance"] / 1000, 2),
        "duration_minutes": round(route["duration"] / 60, 1),
        "mode": mode,
        "provider": "OSRM demo routing service",
        "disclaimer": "An estimate from the routing provider; actual journey time varies with traffic, service conditions and route availability.",
    }
