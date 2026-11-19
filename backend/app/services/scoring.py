"""Transparent weighted scoring with explicit missing-data handling."""

from app.schemas.scoring import (
    ComparisonScoreRequest,
    ComparisonScoreResponse,
    IndicatorBreakdown,
    NeighbourhoodScore,
)

DISCLAIMER = (
    "This is an indicative decision-support score based only on the supplied "
    "normalized inputs. It is not an official rating or a guarantee of "
    "neighbourhood quality. Check sources, dates, coverage, and local conditions."
)


def calculate_comparison(
    request: ComparisonScoreRequest,
) -> ComparisonScoreResponse:
    """Score each area while re-normalizing weights over available indicators.

    Missing values are excluded rather than treated as zero. Coverage is the
    sum of the original weights for indicators actually supplied.
    """
    results: list[NeighbourhoodScore] = []

    for area in request.neighbourhoods:
        breakdown: dict[str, IndicatorBreakdown] = {}
        missing: list[str] = []
        weighted_total = 0.0
        available_weight = 0.0

        for indicator, weight in request.weights.items():
            supplied = area.indicators.get(indicator)
            if supplied is None:
                missing.append(indicator)
                continue

            weighted_total += supplied.value * weight
            available_weight += weight
            breakdown[indicator] = IndicatorBreakdown(
                value=supplied.value,
                weight=weight,
                contribution=round(supplied.value * weight, 4),
                source=supplied.source,
                observed_at=supplied.observed_at,
            )

        score = weighted_total / available_weight if available_weight else 0.0
        results.append(
            NeighbourhoodScore(
                name=area.name,
                score=round(score, 2),
                coverage=round(available_weight * 100, 2),
                indicators_used=len(breakdown),
                indicators_missing=missing,
                breakdown=breakdown,
            )
        )

    results.sort(key=lambda item: item.score, reverse=True)
    return ComparisonScoreResponse(
        methodology=(
            "Weighted mean of supplied 0–100 indicators. Missing indicators are "
            "excluded; available weights are re-normalized. Coverage is the "
            "percentage of the original total weight represented by supplied data."
        ),
        scores=results,
        disclaimer=DISCLAIMER,
    )
