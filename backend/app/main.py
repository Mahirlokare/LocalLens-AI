"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.routes.comparisons import router as comparisons_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Neighbourhood and commute intelligence API.",
    version="0.1.0",
)

app.include_router(comparisons_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return a lightweight service health response."""
    return {"status": "ok", "service": "locallens-api"}
