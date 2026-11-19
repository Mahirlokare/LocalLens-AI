"""India-wide place search and travel-mode route endpoints."""
from fastapi import APIRouter, HTTPException, Query
import httpx

from app.schemas.places import PlaceResult, CommuteRequest, CommuteResponse
from app.services.geo import search_places, suggest_places, estimate_route

router = APIRouter(tags=["places and commute"])


@router.get("/places/suggest", response_model=list[PlaceResult])
async def places_suggest(q: str = Query(min_length=2, max_length=180)):
    """Interactive place suggestions via Photon (not public Nominatim autocomplete)."""
    try:
        return await suggest_places(q)
    except (httpx.HTTPError, ValueError, RuntimeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Place suggestions are temporarily unavailable. You can still use Search to try the alternate provider.",
        ) from exc


@router.get("/places/search", response_model=list[PlaceResult])
async def places_search(q: str = Query(min_length=2, max_length=180)):
    """Search for a place in India using OpenStreetMap Nominatim."""
    try:
        return await search_places(q)
    except (httpx.HTTPError, ValueError, RuntimeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="India place search is temporarily unavailable. Please retry shortly.",
        ) from exc


@router.post("/commute/estimate", response_model=CommuteResponse)
async def commute_estimate(payload: CommuteRequest):
    """Calculate a mapped route for the selected supported travel mode."""
    try:
        return await estimate_route(
            payload.origin_lon, payload.origin_lat,
            payload.destination_lon, payload.destination_lat, payload.mode,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Routing service is temporarily unavailable. Please retry shortly.",
        ) from exc
