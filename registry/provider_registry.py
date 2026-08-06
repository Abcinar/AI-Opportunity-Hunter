"""Provider Registry for Opportunity Intelligence Platform.

This module provides a central registry that stores and manages validated
BaseProvider instances. The registry supports registration, lookup, and
lifecycle management of providers without creating or executing them.
"""

from __future__ import annotations

import logging
from typing import Iterator

from base_provider import BaseProvider

logger = logging.getLogger(__name__)


class ProviderAlreadyRegisteredError(Exception):
    """Raised when attempting to register a provider whose name already exists."""


class ProviderNotFoundError(Exception):
    """Raised when a requested provider name is not present in the registry."""


class ProviderRegistry:
    """Central registry for BaseProvider instances.

    The registry stores provider instances keyed by their unique name.
    Lookup operations are O(1). Duplicate registrations are rejected.
    The registry never instantiates or invokes providers; it only stores
    already-created and validated instances.

    Attributes:
        _providers: Internal mapping of provider name to BaseProvider instance.
    """

    def __init__(self) -> None:
        """Initialize an empty provider registry."""
        self._providers: dict[str, BaseProvider] = {}
        logger.debug("ProviderRegistry initialized")

    def register(self, provider: BaseProvider) -> None:
        """Register a validated provider instance.

        Args:
            provider: A fully constructed BaseProvider instance to store.

        Raises:
            TypeError: If provider is not an instance of BaseProvider.
            ProviderAlreadyRegisteredError: If a provider with the same name
                is already registered.
        """
        if not isinstance(provider, BaseProvider):
            raise TypeError(
                f"Expected BaseProvider instance, got {type(provider).__name__}"
            )
        name = provider.name
        if name in self._providers:
            raise ProviderAlreadyRegisteredError(
                f"Provider '{name}' is already registered"
            )
        self._providers[name] = provider
        logger.info("Registered provider '%s'", name)

    def unregister(self, name: str) -> None:
        """Remove a provider from the registry by name.

        Args:
            name: The unique name of the provider to remove.

        Raises:
            ProviderNotFoundError: If no provider with the given name exists.
        """
        if name not in self._providers:
            raise ProviderNotFoundError(f"Provider '{name}' is not registered")
        del self._providers[name]
        logger.info("Unregistered provider '%s'", name)

    def get(self, name: str) -> BaseProvider:
        """Retrieve a provider by its unique name.

        Args:
            name: The unique name of the provider to retrieve.

        Returns:
            The BaseProvider instance associated with the given name.

        Raises:
            ProviderNotFoundError: If no provider with the given name exists.
        """
        try:
            return self._providers[name]
        except KeyError:
            raise ProviderNotFoundError(
                f"Provider '{name}' is not registered"
            ) from None

    def get_all(self) -> list[BaseProvider]:
        """Return a list of all registered providers.

        Returns:
            A new list containing every BaseProvider currently stored
            in the registry. The order is insertion order.
        """
        return list(self._providers.values())

    def exists(self, name: str) -> bool:
        """Check whether a provider with the given name is registered.

        Args:
            name: The unique name to test.

        Returns:
            True if a provider with the given name is present, False otherwise.
        """
        return name in self._providers

    def count(self) -> int:
        """Return the number of currently registered providers.

        Returns:
            The count of providers stored in the registry.
        """
        return len(self._providers)

    def clear(self) -> None:
        """Remove all providers from the registry.

        After this call the registry is empty. No exceptions are raised.
        """
        self._providers.clear()
        logger.info("ProviderRegistry cleared")

    def __contains__(self, name: str) -> bool:
        """Support the ``in`` operator for existence checks.

        Args:
            name: Provider name to test.

        Returns:
            True if the name is registered, False otherwise.
        """
        return self.exists(name)

    def __len__(self) -> int:
        """Return the number of registered providers.

        Returns:
            Integer count of providers.
        """
        return self.count()

    def __iter__(self) -> Iterator[BaseProvider]:
        """Iterate over all registered providers.

        Yields:
            Each BaseProvider instance currently stored in the registry.
        """
        return iter(self._providers.values())
