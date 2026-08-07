"""
pipeline.py

Orchestration layer for Intelligence Engines in the
Opportunity Intelligence Platform (OIP).

This module replaces the legacy analyze_signals() implementation.
It contains only sequencing logic; no business rules, scoring formulas
or recommendation logic belong here.
"""

from __future__ import annotations

from typing import Any

from .category_engine import CategoryEngine
from .score_engine import ScoreEngine

__all__ = [
    "analyze_signal",
    "analyze_signals",
]

# ---------------------------------------------------------------------------
# Engine instances (created once)
# ---------------------------------------------------------------------------

_category_engine = CategoryEngine()
_score_engine = ScoreEngine()

# TODO: _confidence_engine = ConfidenceEngine()
# TODO: _founder_fit_engine = FounderFitEngine()
# TODO: _recommendation_engine = RecommendationEngine()

_ENGINES = (
    _category_engine,
    _score_engine,
)

# Future engines:
# - ConfidenceEngine
# - FounderFitEngine
# - RecommendationEngine

def analyze_signal(opportunity: Any) -> Any:
    """
    Run the full intelligence pipeline on a single opportunity.

    Order
    -----
    1. CategoryEngine
    2. ScoreEngine
    3. ConfidenceEngine      (TODO)
    4. FounderFitEngine      (TODO)
    5. RecommendationEngine  (TODO)

    Parameters
    ----------
    opportunity : Any
        Opportunity instance (dict or object).

    Returns
    -------
    Any
        The enriched opportunity.
    """
    for engine in _ENGINES:
        opportunity = engine.process(opportunity)
    return opportunity


def analyze_signals(opportunities: list[Any]) -> list[Any]:
    """
    Run the intelligence pipeline on a list of opportunities.

    Parameters
    ----------
    opportunities : list[Any]
        List of opportunity instances (dict or object).

    Returns
    -------
    list[Any]
        List of enriched opportunities (same order).
    """
    return [analyze_signal(opportunity) for opportunity in opportunities]
