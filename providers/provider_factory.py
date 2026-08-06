"""Provider Factory for Opportunity Intelligence Platform.

Responsible solely for constructing concrete Provider instances from a
provider name and a ProviderConfig. Contains no registry, networking,
or side-effect logic.
"""

from __future__ import annotations

from providers.base_provider import BaseProvider
from providers.github_provider import GitHubProvider
from providers.hackernews_provider import HackerNewsProvider
from providers.provider_config import ProviderConfig


class ProviderFactory:
    """Factory that creates concrete Provider instances.

    The factory knows how to map a provider name to its implementation
    and how to wire a ProviderConfig into the constructor. It performs
    no registration, caching, or execution of providers.
    """

    @staticmethod
    def create(provider_name: str, config: ProviderConfig) -> BaseProvider:
        """Create a Provider instance for the given name and configuration.

        Args:
            provider_name: Case-insensitive identifier of the provider
                (e.g. \"github\").
            config: Immutable configuration object to inject.

        Returns:
            A fully constructed BaseProvider subclass instance.

        Raises:
            ValueError: If provider_name is not recognised.
            TypeError: If config is not a ProviderConfig instance.
        """
        if not isinstance(config, ProviderConfig):
            raise TypeError(
                f"Expected ProviderConfig, got {type(config).__name__}"
            )

        name = provider_name.strip().lower()

        if name == "github":
            return GitHubProvider(
                token=config.token,
                enabled=config.enabled,
                timeout=config.timeout,
                default_query=config.default_query,
                per_page=config.per_page,
                sort=config.sort,
                order=config.order,
            )

        elif name == "hackernews":
            return HackerNewsProvider(
                token=config.token,
                enabled=config.enabled,
                timeout=config.timeout,
                default_query=config.default_query,
                per_page=config.per_page,
                sort=config.sort,
                order=config.order,
            )

        else:
            raise ValueError(f"Unknown provider: '{provider_name}'")


__all__ = ["ProviderFactory"]
