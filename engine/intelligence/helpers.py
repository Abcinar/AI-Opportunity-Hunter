"""
helpers.py
__all__ = [
    "get_field",
    "set_field",
    "read_float",
    "normalize_text",
    "clamp",
]
Reusable helper functions for Intelligence Engines in the
Opportunity Intelligence Platform (OIP).

This module contains only pure utility functions.
No classes, business logic, scoring or category logic is permitted.
All functions safely support both dictionary and object opportunities.
"""

from __future__ import annotations

from typing import Any


def get_field(opportunity: Any, name: str) -> Any:
    """
    Retrieve a field from an opportunity.

    Supports both plain dictionaries and attribute-style objects.
    Missing fields return None; no exception is raised.
    """
    if isinstance(opportunity, dict):
        return opportunity.get(name)
    return getattr(opportunity, name, None)


def set_field(opportunity: Any, name: str, value: Any) -> None:
    """
    Set a field on an opportunity.

    Supports both plain dictionaries and attribute-style objects.
    """
    if isinstance(opportunity, dict):
        opportunity[name] = value
    else:
        setattr(opportunity, name, value)


def read_float(opportunity: Any, name: str) -> float:
    """
    Safely read a numeric field as float.

    Missing, None or non-numeric values return 0.0.
    """
    value = get_field(opportunity, name)
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def normalize_text(opportunity: Any) -> str:
    """
    Extract and normalize textual content from an opportunity.

    Reads title, description, summary and content.
    - Ignores None values
    - Strips whitespace
    - Converts the concatenated result to lowercase
    """
    fields = ("title", "description", "summary", "content")
    parts: list[str] = []

    for field in fields:
        value = get_field(opportunity, field)
        if value is not None and isinstance(value, str):
            stripped = value.strip()
            if stripped:
                parts.append(stripped)

    return " ".join(parts).lower()


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    """
    Clamp a numeric value into the closed interval [minimum, maximum].
    """
    return max(minimum, min(maximum, value))
