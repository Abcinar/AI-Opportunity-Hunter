"""Provider Configuration for Opportunity Intelligence Platform.

Immutable configuration object injected into every concrete Provider.
Contains only data; no I/O, logging, or provider logic.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    """Immutable configuration contract shared by all providers.

    All values are validated at construction time. The instance cannot be
    mutated after creation.

    Attributes:
        token: Authentication secret (PAT, API key, etc.).
        base_url: Root URL of the external API (must use HTTPS).
        timeout: Maximum seconds allowed for a single network operation.
        enabled: Master switch; when False the Provider must refuse to operate.
        default_query: Default search or filter expression used by fetch().
        per_page: Page size for list/search endpoints (1–100).
        sort: Sort field for search results.
        order: Sort order (\"asc\" or \"desc\").
    """

    token: str
    base_url: str
    timeout: float
    enabled: bool
    default_query: str
    per_page: int
    sort: str
    order: str

    def __post_init__(self) -> None:
        """Validate all fields after initialization.

        Raises:
            ValueError: If any field violates the configuration contract.
        """
        if not self.token or not self.token.strip():
            raise ValueError("token must be a non-empty string")
        if not self.base_url or not self.base_url.strip():
            raise ValueError("base_url must be a non-empty string")
        if not self.base_url.startswith("https://"):
            raise ValueError("base_url must start with https://")
        if self.timeout <= 0:
            raise ValueError("timeout must be greater than 0")
        if not self.default_query or not self.default_query.strip():
            raise ValueError("default_query must be a non-empty string")
        if not isinstance(self.per_page, int) or self.per_page < 1 or self.per_page > 100:
            raise ValueError("per_page must be an integer in the range [1, 100]")
        if not self.sort or not self.sort.strip():
            raise ValueError("sort must be a non-empty string")
        if self.order not in ("asc", "desc"):
            raise ValueError("order must be 'asc' or 'desc'")


__all__ = ["ProviderConfig"]
