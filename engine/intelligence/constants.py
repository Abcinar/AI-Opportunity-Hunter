"""
constants.py

Shared constants for the Opportunity Intelligence Platform (OIP).

This module contains only immutable shared values.
No business logic, functions, classes or calculations are permitted.
"""

__all__ = [
    "DEFAULT_SCORE",
    "DEFAULT_CONFIDENCE",
    "DEFAULT_FOUNDER_FIT",
    "UNKNOWN_CATEGORY",
    "UNKNOWN_SUBCATEGORY",
    "RECOMMENDATION_BUILD",
    "RECOMMENDATION_VALIDATE",
    "RECOMMENDATION_WATCH",
    "RECOMMENDATION_IGNORE",
]

DEFAULT_SCORE: float = 0.0
DEFAULT_CONFIDENCE: float = 0.0
DEFAULT_FOUNDER_FIT: float = 0.0

UNKNOWN_CATEGORY: str = "Unknown"
UNKNOWN_SUBCATEGORY: str = "Unknown"

RECOMMENDATION_BUILD: str = "BUILD"
RECOMMENDATION_VALIDATE: str = "VALIDATE"
RECOMMENDATION_WATCH: str = "WATCH"
RECOMMENDATION_IGNORE: str = "IGNORE"
