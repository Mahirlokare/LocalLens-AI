"""Tests for neighbourhood scoring and missing-data behavior."""

import pytest
from pydantic import ValidationError

from app.schemas.scoring import ComparisonScoreRequest
from app.services.scoring import calculate_comparison


def test_weighted_score_and_sorting():
    """Higher weighted scores should be returned first."""
    payload = ComparisonScoreRequest.model_validate(
        {
            "weights": {"healthcare": 0.6, "transit": 0.4},
            "neighbourhoods": [
                {
                    "name": "Area A",
                    "indicators": {
                        "healthcare": {"value": 80, "source": "dataset-a", "observed_at": "2026-11-01"},
                        "transit": {"value": 60, "source": "dataset-b", "observed_at": "2026-11-01"},
                    },
                },
                {
                    "name": "Area B",
                    "indicators": {
                        "healthcare": {"value": 50, "source": "dataset-a", "observed_at": "2026-11-01"},
                        "transit": {"value": 50, "source": "dataset-b", "observed_at": "2026-11-01"},
                    },
                },
            ],
        }
    )

    result = calculate_comparison(payload)

    assert result.scores[0].name == "Area A"
    assert result.scores[0].score == 72.0
    assert result.scores[1].score == 50.0


def test_missing_indicator_is_not_treated_as_zero():
    """Available weights are re-normalized and coverage is reported."""
    payload = ComparisonScoreRequest.model_validate(
        {
            "weights": {"healthcare": 0.5, "transit": 0.5},
            "neighbourhoods": [
                {
                    "name": "Area A",
                    "indicators": {
                        "healthcare": {"value": 80, "source": "dataset-a", "observed_at": "2026-11-01"}
                    },
                }
            ],
        }
    )

    result = calculate_comparison(payload)
    score = result.scores[0]

    assert score.score == 80.0
    assert score.coverage == 50.0
    assert score.indicators_missing == ["transit"]


def test_weights_must_sum_to_one():
    """Invalid weight totals should fail validation."""
    with pytest.raises(ValidationError):
        ComparisonScoreRequest.model_validate(
            {
                "weights": {"healthcare": 0.7, "transit": 0.2},
                "neighbourhoods": [{"name": "Area A", "indicators": {}}],
            }
        )
