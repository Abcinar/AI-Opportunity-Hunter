"""
score_engine.py

Score calculation engine for the Opportunity Intelligence Platform (OIP).

Responsibilities
----------------
- Read currently available metrics (engagement, momentum)
- Apply immutable weights from weights.py
- Compute opportunity_score
- Clamp the result to the closed interval [0, 100]
- Enrich and return the Opportunity

Future metrics (source_quality, category_value, founder_fit_modifier)
are intentionally excluded until the upstream pipeline produces them.
"""

from __future__ import annotations

from typing import Any

from .base_engine import BaseEngine
from .helpers import clamp, read_float, set_field
from .weights import (
    ENGAGEMENT_WEIGHT,
    MOMENTUM_WEIGHT,
)

# Future metrics will be introduced in later pipeline stages:
# - SOURCE_WEIGHT
# - CATEGORY_WEIGHT
# - FOUNDER_FIT_WEIGHT


class ScoreEngine(BaseEngine):
    """
    Weighted scoring engine that produces a single opportunity_score
    from currently available metrics.
    """

    def process(self, opportunity: Any) -> Any:
        """
        Calculate opportunity_score and attach it to the Opportunity.

        Supports both attribute-style objects and plain dictionaries.
        """
        engagement = read_float(opportunity, "engagement")
        momentum = read_float(opportunity, "momentum")

        # TODO: source_quality = read_float(opportunity, "source_quality")
        # TODO: category_value = read_float(opportunity, "category_value")
        # TODO: founder_fit_modifier = read_float(opportunity, "founder_fit_modifier")

        raw_score = (
            engagement * ENGAGEMENT_WEIGHT
            + momentum * MOMENTUM_WEIGHT
            # TODO: + source_quality * SOURCE_WEIGHT
            # TODO: + category_value * CATEGORY_WEIGHT
            # TODO: + founder_fit_modifier * FOUNDER_FIT_WEIGHT
        )

        score = clamp(raw_score)
        set_field(opportunity, "opportunity_score", score)

        return opportunity
