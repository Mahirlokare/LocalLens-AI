"""Geocoding and commute endpoints."""
from fastapi import APIRouter, HTTPException, Query
import httpx

from app.schemas.places import PlaceResult, CommuteRequest, CommuteResponse
from app.services.geo import search_places, estimate_route

router = APIRouter(tags=["places and commute"])


@router.get("/places/search", response_model=list[PlaceResult])
async def places_search(q: str = Query(min_length=2, max_length=180)):
    """Search a place using OpenStreetMap Nominatim."""
    try:
        return await search_places(q)
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="Place search provider is temporarily unavailable.") from exc


@router.post("/commute/estimate", response_model=CommuteResponse)
async def commute_estimate(payload: CommuteRequest):
    """Estimate distance and duration between two coordinates."""
    try:
        return await estimate_route(
            payload.origin_lon, payload.origin_lat,
            payload.destination_lon, payload.destination_lat, payload.mode,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Routing provider is temporarily unavailable.") from exc
