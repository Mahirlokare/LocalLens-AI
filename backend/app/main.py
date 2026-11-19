"""FastAPI application entry point."""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.comparisons import router as comparisons_router
from app.api.routes.places import router as places_router
from app.api.routes.neighbourhoods import router as neighbourhoods_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Neighbourhood and commute intelligence API.",
    version="0.2.0",
)

# Configure production frontend origins through CORS_ORIGINS (comma-separated).
# Local development origins remain available by default.
_default_origins = "http://localhost:5173,http://127.0.0.1:5173"
_allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", _default_origins).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(comparisons_router, prefix=settings.api_v1_prefix)
app.include_router(places_router, prefix=settings.api_v1_prefix)
app.include_router(neighbourhoods_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return a lightweight service health response."""
    return {"status": "ok", "service": "locallens-api"}
