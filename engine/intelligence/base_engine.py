"""
Base Engine

Defines the abstract contract for every Intelligence Engine.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseEngine(ABC):
    """Base class for all Intelligence Engines."""

    @abstractmethod
    def process(self, opportunity: Any) -> Any:
        """
        Process an opportunity.

        Parameters
        ----------
        opportunity
            Opportunity to process.

        Returns
        -------
        Processed opportunity.
        """
        raise NotImplementedError
