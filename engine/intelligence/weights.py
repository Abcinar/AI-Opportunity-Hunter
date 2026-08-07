"""
weights.py

Immutable scoring weights for the Opportunity Intelligence Platform (OIP).

This module contains only constant weight definitions.
No functions, classes or business logic are permitted.
All weights sum exactly to 1.0.
"""

__all__ = [
    "ENGAGEMENT_WEIGHT",
    "MOMENTUM_WEIGHT",
    "SOURCE_WEIGHT",
    "CATEGORY_WEIGHT",
    "FOUNDER_FIT_WEIGHT",
]

ENGAGEMENT_WEIGHT: float = 0.35
MOMENTUM_WEIGHT: float = 0.25
SOURCE_WEIGHT: float = 0.15
CATEGORY_WEIGHT: float = 0.10
FOUNDER_FIT_WEIGHT: float = 0.15
