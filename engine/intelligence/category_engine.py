"""
category_engine.py

Category orchestration engine for the
Opportunity Intelligence Platform (OIP).

This engine is responsible only for the category classification
workflow. Classification rules will be implemented in a future
Rule Layer.
"""

from typing import Any

from .base_engine import BaseEngine


class CategoryEngine(BaseEngine):
    """Category classification orchestration engine."""

    def process(self, opportunity: Any) -> Any:
        """
        Process an opportunity.

        Classification logic will be implemented by the
        Rule Layer in a future sprint.

        Parameters
        ----------
        opportunity : Any
            Opportunity to process.

        Returns
        -------
        Any
            The same opportunity instance.
        """
        return opportunity
