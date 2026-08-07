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
# Future metrics will be introduced in later pipeline stages:
# - SOURCE_WEIGHT
# - CATEGORY_WEIGHT
# - FOUNDER_FIT_WEIGHT
from typing import Any

from .base_engine import BaseEngine
from .weights import (
    ENGAGEMENT_WEIGHT,
    MOMENTUM_WEIGHT,
)


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
        engagement = self._read_metric(opportunity, "engagement")
        momentum = self._read_metric(opportunity, "momentum")

        # TODO: source_quality = self._read_metric(opportunity, "source_quality")
        # TODO: category_value = self._read_metric(opportunity, "category_value")
        # TODO: founder_fit_modifier = self._read_metric(opportunity, "founder_fit_modifier")

        raw_score = (
            engagement * ENGAGEMENT_WEIGHT
            + momentum * MOMENTUM_WEIGHT
            # TODO: + source_quality * SOURCE_WEIGHT
            # TODO: + category_value * CATEGORY_WEIGHT
            # TODO: + founder_fit_modifier * FOUNDER_FIT_WEIGHT
        )

        score = self._clamp(raw_score)
        self._set_field(opportunity, "opportunity_score", score)

        return opportunity

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _read_metric(self, opportunity: Any, name: str) -> float:
        """
        Safely read a numeric metric.

        Missing or non-numeric values default to 0.0.
        """
        value = self._get_field(opportunity, name)
        if value is None:
            return 0.0
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _clamp(self, value: float) -> float:
        """Clamp a score into the closed interval [0, 100]."""
        return max(0.0, min(100.0, value))

    def _get_field(self, opportunity: Any, name: str) -> Any:
        """Retrieve a field from either an object or a dict."""
        if isinstance(opportunity, dict):
            return opportunity.get(name)
        return getattr(opportunity, name, None)

    def _set_field(self, opportunity: Any, name: str, value: Any) -> None:
        """Set a field on either an object or a dict."""
        if isinstance(opportunity, dict):
            opportunity[name] = value
        else:
            setattr(opportunity, name, value)
