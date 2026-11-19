"""Schemas for India-wide place search and route estimates."""
from pydantic import BaseModel, Field


class PlaceResult(BaseModel):
    display_name: str
    latitude: float
    longitude: float
    category: str | None = None


class CommuteRequest(BaseModel):
    origin_lat: float = Field(ge=-90, le=90)
    origin_lon: float = Field(ge=-180, le=180)
    destination_lat: float = Field(ge=-90, le=90)
    destination_lon: float = Field(ge=-180, le=180)
    mode: str = Field(default="driving", pattern="^(driving|motorcycle|scooter|cycling|walking)$")


class CommuteResponse(BaseModel):
    distance_km: float
    duration_minutes: float
    mode: str
    geometry: str = ""
    provider: str
    disclaimer: str
