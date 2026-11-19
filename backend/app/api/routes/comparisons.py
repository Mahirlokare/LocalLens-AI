"""Neighbourhood comparison endpoints."""

from fastapi import APIRouter

from app.schemas.scoring import ComparisonScoreRequest, ComparisonScoreResponse
from app.services.scoring import calculate_comparison

router = APIRouter(prefix="/comparisons", tags=["comparisons"])


@router.post("/score", response_model=ComparisonScoreResponse)
def score_neighbourhoods(
    payload: ComparisonScoreRequest,
) -> ComparisonScoreResponse:
    """Calculate a transparent score from caller-supplied indicator data."""
    return calculate_comparison(payload)
