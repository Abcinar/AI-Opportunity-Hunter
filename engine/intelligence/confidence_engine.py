"""
confidence_engine.py
====================

Confidence Engine for the Opportunity Intelligence Platform (OIP).

Responsibility
--------------
Estimate how trustworthy an opportunity signal is.

This engine MUST NOT:
- classify categories
- calculate opportunity score
- generate recommendations

It only produces a confidence score.
"""

from __future__ import annotations

from typing import Any

from .contracts import EngineContract
from ..rules.confidence_rules import (
    SOURCE_RELIABILITY,
    REQUIRED_FIELDS,
    CONFIDENCE_LEVELS,
    SOURCE_WEIGHT,
    COMPLETENESS_WEIGHT,
    FRESHNESS_WEIGHT,
)


class ConfidenceEngine(EngineContract):
    """Estimate confidence for an opportunity."""

    def process(self, opportunity: Any) -> Any:
        source_score = self._source_score(opportunity)
        completeness_score = self._completeness_score(opportunity)
        freshness_score = self._freshness_score(opportunity)

        confidence = (
            source_score * SOURCE_WEIGHT
            + completeness_score * COMPLETENESS_WEIGHT
            + freshness_score * FRESHNESS_WEIGHT
        )

        confidence = round(confidence, 2)

        opportunity["confidence"] = confidence
        opportunity["confidence_level"] = self._confidence_level(confidence)

        return opportunity

    # ------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------

    def _source_score(self, opportunity: Any) -> float:
        source = str(opportunity.get("source", "")).lower()

        return SOURCE_RELIABILITY.get(source, 50)

    def _completeness_score(self, opportunity: Any) -> float:
        completed = sum(
            1
            for field in REQUIRED_FIELDS
            if opportunity.get(field)
        )

        return (completed / len(REQUIRED_FIELDS)) * 100

    def _freshness_score(self, opportunity: Any) -> float:
        """
        Placeholder.

        Freshness analysis will be implemented when
        timestamp normalization is available.
        """

        return 100.0

    def _confidence_level(self, confidence: float) -> str:
        for level, (minimum, maximum) in CONFIDENCE_LEVELS.items():
            if minimum <= confidence < maximum:
                return level

        return "VERY_HIGH"
