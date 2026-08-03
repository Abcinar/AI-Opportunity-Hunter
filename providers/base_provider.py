"""Base Provider Contract for AI Opportunity Hunter (V2).

This module defines the abstract base class that every concrete provider
must inherit from. It establishes the provider contract and belongs
exclusively to the Provider layer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from types import MappingProxyType
from typing import Any, Sequence


class BaseProvider(ABC):
    """Abstract base class defining the Provider Contract (V2).

    Every concrete Provider implementation MUST inherit from this class.
    The class cannot be instantiated directly. It exposes required metadata
    via read-only properties and the minimal set of abstract methods that
    form the provider contract.

    Identity and configuration fields are stored privately and exposed only
    through read-only properties to prevent accidental mutation at runtime.
    """

    __slots__ = (
        "_id",
        "_display_name",
        "_description",
        "_version",
        "_category",
        "_enabled",
        "_timeout",
        "_capabilities",
    )

    def __init__(
        self,
        id: str,
        display_name: str,
        description: str,
        version: str,
        category: str,
        enabled: bool,
        timeout: float,
        capabilities: Sequence[str],
    ) -> None:
        """Initialize provider metadata.

        Args:
            id: Unique identifier of the provider.
            display_name: Human-readable name shown in UIs.
            description: Short description of the provider purpose.
            version: Semantic version string of the provider implementation.
            category: Logical category (e.g. "social", "code", "trends").
            enabled: Whether the provider is active.
            timeout: Maximum seconds allowed for a single fetch operation.
            capabilities: List of capability identifiers supported by the provider.

        Raises:
            ValueError: If id is empty or timeout is not positive.
        """
        if not id or not id.strip():
            raise ValueError("id must be a non-empty string")
        if timeout <= 0:
            raise ValueError("timeout must be greater than 0")

        self._id = id.strip()
        self._display_name = display_name
        self._description = description
        self._version = version
        self._category = category
        self._enabled = enabled
        self._timeout = timeout
        self._capabilities = tuple(capabilities)

    @property
    def id(self) -> str:
        """Unique identifier of the provider."""
        return self._id

    @property
    def display_name(self) -> str:
        """Human-readable name shown in UIs."""
        return self._display_name

    @property
    def description(self) -> str:
        """Short description of the provider purpose."""
        return self._description

    @property
    def version(self) -> str:
        """Semantic version string of the provider implementation."""
        return self._version

    @property
    def category(self) -> str:
        """Logical category (e.g. \"social\", \"code\", \"trends\")."""
        return self._category

    @property
    def enabled(self) -> bool:
        """Whether the provider is active."""
        return self._enabled

    @property
    def timeout(self) -> float:
        """Maximum seconds allowed for a single fetch operation."""
        return self._timeout

    @property
    def capabilities(self) -> Sequence[str]:
        """List of capability identifiers supported by the provider."""
        return self._capabilities

    @property
    def metadata(self) -> MappingProxyType[str, Any]:
        """Return the complete provider metadata as an immutable mapping.

        Returns:
            A read-only mapping containing all required metadata fields.
        """
        return MappingProxyType(
            {
                "id": self.id,
                "display_name": self.display_name,
                "description": self.description,
                "version": self.version,
                "category": self.category,
                "enabled": self.enabled,
                "timeout": self.timeout,
                "capabilities": list(self.capabilities),
            }
        )

    @abstractmethod
    def fetch(self) -> Any:
        """Retrieve raw data from the external source.

        Returns:
            Provider-specific raw data. The concrete type is intentionally
            left open so that different sources (GitHub, Reddit, Trends, etc.)
            can return their natural shapes. Normalization is handled later
            by the Normalizer layer.

        Raises:
            Exception: Any error encountered while fetching data.
        """

    @abstractmethod
    def validate(self) -> bool:
        """Validate the provider configuration and readiness.

        Returns:
            True if the provider is correctly configured and ready to
            perform fetch operations, False otherwise.

        Raises:
            Exception: Unexpected internal errors that prevent validation.
        """

    @abstractmethod
    def health_check(self) -> bool:
        """Verify that the external data source is reachable and healthy.

        Returns:
            True if the provider can successfully communicate with its
            external source, False otherwise. Ordinary unavailability
            must return False rather than raise.

        Raises:
            Exception: Only for unexpected internal errors that prevent
                the health check itself from executing.
        """


__all__ = ["BaseProvider"]
