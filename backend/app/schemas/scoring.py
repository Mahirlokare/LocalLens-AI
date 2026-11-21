"""Request and response contracts for neighbourhood scoring."""

from pydantic import BaseModel, Field, model_validator


class IndicatorValue(BaseModel):
    """A normalized indicator value and its provenance."""

    value: float = Field(ge=0, le=100, description="Normalized score from 0 to 100")
    source: str = Field(min_length=1, max_length=300)
    observed_at: str = Field(min_length=1, max_length=64)


class NeighbourhoodInput(BaseModel):
    """Indicator values supplied for one neighbourhood."""

    name: str = Field(min_length=1, max_length=120)
    indicators: dict[str, IndicatorValue]


class ComparisonScoreRequest(BaseModel):
    """Neighbourhoods and criterion weights for a comparison."""

    neighbourhoods: list[NeighbourhoodInput] = Field(min_length=2, max_length=3, description="Compare between two and three localities at a time.")
    weights: dict[str, float]

    @model_validator(mode="after")
    def validate_weights(self):
        """Require non-negative weights that sum to one."""
        # Enforce distinct localities at the API boundary, not only in the UI.
        names = [area.name.strip().casefold() for area in self.neighbourhoods]
        if len(names) != len(set(names)):
            raise ValueError("Each locality must be unique in a comparison.")
        if not self.weights:
            raise ValueError("At least one indicator weight is required.")
        if any(weight < 0 for weight in self.weights.values()):
            raise ValueError("Weights cannot be negative.")
        if abs(sum(self.weights.values()) - 1.0) > 1e-6:
            raise ValueError("Indicator weights must sum to 1.0.")
        if any(not key.strip() for key in self.weights):
            raise ValueError("Indicator names cannot be blank.")
        return self


class IndicatorBreakdown(BaseModel):
    value: float
    weight: float
    contribution: float
    source: str
    observed_at: str


class NeighbourhoodScore(BaseModel):
    name: str
    score: float
    coverage: float
    indicators_used: int
    indicators_missing: list[str]
    breakdown: dict[str, IndicatorBreakdown]


class ComparisonScoreResponse(BaseModel):
    methodology: str
    scores: list[NeighbourhoodScore]
    disclaimer: str
