"""
contracts.py

Shared structural contracts for Intelligence Engines in the
Opportunity Intelligence Platform (OIP).

This module defines only typing contracts.
No business logic, calculations, scoring, recommendation or
category logic is permitted.
"""

from __future__ import annotations

from typing import Any, Protocol

__all__ = ["EngineContract"]


class EngineContract(Protocol):
    """
    Structural contract that every Intelligence Engine must satisfy.
    """

    def process(self, opportunity: Any) -> Any:
        """
        Process an opportunity and return the processed opportunity.
        """
        ...
