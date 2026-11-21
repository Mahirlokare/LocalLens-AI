"""Validated contracts for the LocalLens AI assistant."""

from pydantic import BaseModel, Field


class LocalityContext(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    city: str = Field(default="", max_length=160)
    description: str = Field(default="", max_length=1200)
    indicators: dict[str, dict] = Field(default_factory=dict)


class AIRecommendationRequest(BaseModel):
    question: str = Field(min_length=5, max_length=1200)
    budget_inr: int | None = Field(default=None, ge=0, le=10000000)
    priorities: list[str] = Field(default_factory=list, max_length=8)
    localities: list[LocalityContext] = Field(min_length=1, max_length=40)


class AIRecommendationResponse(BaseModel):
    answer: str
    model: str
    evidence_note: str
