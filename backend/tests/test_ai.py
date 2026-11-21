"""Tests for grounded LocalLens AI recommendations and the free NLP fallback."""

import asyncio

from app.api.routes.ai import recommend_localities
from app.schemas.ai import AIRecommendationRequest


def test_local_tfidf_fallback_matches_relevant_locality(monkeypatch):
    """The no-key fallback should rank relevant locality descriptions."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    payload = AIRecommendationRequest.model_validate({
        "question": "I need good public transport and metro connectivity",
        "priorities": ["Public transport"],
        "localities": [
            {
                "name": "Transit Hub",
                "city": "City A",
                "description": "Excellent metro station access and frequent public transport connections.",
                "indicators": {},
            },
            {
                "name": "Quiet Enclave",
                "city": "City B",
                "description": "Quiet residential streets and green surroundings.",
                "indicators": {},
            },
        ],
    })

    result = asyncio.run(recommend_localities(payload))

    assert result.model == "tfidf-content-matcher"
    assert "Transit Hub" in result.answer
    assert "not a prediction" in result.answer


def test_local_tfidf_fallback_discloses_missing_evidence(monkeypatch):
    """The fallback must not invent a ranking when locality data is absent."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    payload = AIRecommendationRequest.model_validate({
        "question": "Which locality should I choose?",
        "localities": [{"name": "Unknown Area", "city": "Unknown City"}],
    })

    result = asyncio.run(recommend_localities(payload))

    assert result.model == "tfidf-content-matcher"
    assert "don't have enough" in result.answer
