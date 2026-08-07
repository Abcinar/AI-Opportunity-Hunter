"""
confidence_rules.py
===================

Immutable confidence scoring rules for the
Opportunity Intelligence Platform (OIP).

This module contains only static confidence-related rules.
No classes, functions or business logic are allowed.
"""

# ---------------------------------------------------------------------------
# Source Reliability
# ---------------------------------------------------------------------------

SOURCE_RELIABILITY = {
    "github": 95,
    "hackernews": 90,
    "reddit": 80,
    "google_trends": 75,
    "twitter": 60,
}

# ---------------------------------------------------------------------------
# Data Completeness
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = (
    "title",
    "description",
    "source",
)

# ---------------------------------------------------------------------------
# Confidence Levels
# ---------------------------------------------------------------------------

CONFIDENCE_LEVELS = {
    "VERY_LOW": (0, 20),
    "LOW": (20, 40),
    "MEDIUM": (40, 60),
    "HIGH": (60, 80),
    "VERY_HIGH": (80, 100),
}

# ---------------------------------------------------------------------------
# Confidence Weights
# ---------------------------------------------------------------------------

SOURCE_WEIGHT = 0.50
COMPLETENESS_WEIGHT = 0.30
FRESHNESS_WEIGHT = 0.20
