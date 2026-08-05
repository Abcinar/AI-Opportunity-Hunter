"""Hacker News Provider V2 for AI Opportunity Hunter.

Concrete implementation of BaseProvider that retrieves raw opportunity
signals from the official Hacker News Firebase API. Returns unprocessed JSON only.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from providers.base_provider import BaseProvider


class HackerNewsProviderError(Exception):
    """Base exception for all HackerNewsProvider failures."""


class HackerNewsAPIError(HackerNewsProviderError):
    """Raised for non-success Hacker News API errors."""


class HackerNewsProvider(BaseProvider):
    """Provider that fetches raw data from the Hacker News Firebase API.

    Configuration is injected at construction time.
    The provider never normalizes, scores, or scrapes HTML.
    """

    _API_BASE = "https://hacker-news.firebaseio.com/v0"
    _ALLOWED_FEEDS = (
        "topstories",
        "newstories",
        "beststories",
        "askstories",
        "showstories",
        "jobstories",
    )

    def __init__(
        self,
        token: str = "",
        *,
        enabled: bool = True,
        timeout: float = 10.0,
        default_query: str = "topstories",
        per_page: int = 30,
        sort: str = "rank",
        order: str = "desc",
    ) -> None:
        """Initialize the Hacker News provider.

        Args:
            token: Ignored. The Hacker News API requires no authentication.
            enabled: Whether the provider is active.
            timeout: Request timeout in seconds.
            default_query: Feed name used by fetch() (e.g. \"topstories\").
            per_page: Maximum number of items to retrieve (1–100).
            sort: Unused; retained for constructor compatibility.
            order: Unused; retained for constructor compatibility.
        """
        super().__init__(
            id="hackernews",
            display_name="Hacker News",
            description="Raw opportunity signals from Hacker News Firebase API",
            version="2.0.0",
            category="news",
            enabled=enabled,
            timeout=timeout,
            capabilities=["story_list", "item_details"],
        )
        self._token = token
        self._default_query = default_query
        self._per_page = min(max(per_page, 1), 100)
        self._sort = sort
        self._order = order

    def _build_headers(self) -> dict[str, str]:
        """Build the standard request headers."""
        return {
            "Accept": "application/json",
            "User-Agent": "AI-Opportunity-Hunter/2.0",
        }

    def _request(self, path: str, params: dict[str, str] | None = None) -> Any:
        """Execute a GET request against the Hacker News Firebase API.

        Args:
            path: API path beginning with '/'.
            params: Optional query parameters.

        Returns:
            Parsed JSON response body.

        Raises:
            HackerNewsAPIError: For non-success status codes.
            TimeoutError: When the request exceeds the configured timeout.
            urllib.error.URLError: On network-level failures.
        """
        url = f"{self._API_BASE}{path}"
        if params:
            query = urllib.parse.urlencode(params)
            url = f"{url}?{query}"

        request = urllib.request.Request(
            url,
            headers=self._build_headers(),
            method="GET",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as exc:
            raise HackerNewsAPIError(
                f"Hacker News API error (HTTP {exc.code}): {exc.reason}"
            ) from exc
        except TimeoutError as exc:
            raise TimeoutError(
                f"Hacker News request timed out after {self.timeout}s"
            ) from exc
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, TimeoutError):
                raise TimeoutError(
                    f"Hacker News request timed out after {self.timeout}s"
                ) from exc
            raise

    def fetch(self) -> Any:
        """Retrieve raw story items from Hacker News.

        Returns:
            A list of unprocessed JSON item objects returned by the
            /item/{id}.json endpoints for the selected feed.

        Raises:
            RuntimeError: If the provider is disabled.
            HackerNewsAPIError: For API errors.
            TimeoutError: When the request times out.
            ValueError: If the configured feed name is not allowed.
        """
        if not self.enabled:
            raise RuntimeError("HackerNewsProvider is disabled")

        feed = self._default_query.strip().lower()
        if feed not in self._ALLOWED_FEEDS:
            raise ValueError(
                f"Invalid feed '{feed}'. Allowed: {', '.join(self._ALLOWED_FEEDS)}"
            )

        story_ids = self._request(f"/{feed}.json")
        if not isinstance(story_ids, list):
            raise HackerNewsAPIError("Story list response is not a JSON array")

        selected_ids = story_ids[: self._per_page]
        items: list[Any] = []
        for item_id in selected_ids:
            item = self._request(f"/item/{item_id}.json")
            if item is not None:
                items.append(item)
        return items

    def validate(self) -> bool:
        """Validate provider configuration and readiness.

        Returns:
            True if the provider is enabled and configuration values are
            valid; False otherwise.
        """
        if not self.enabled:
            return False
        if self.timeout <= 0:
            return False
        if self._per_page < 1 or self._per_page > 100:
            return False
        feed = self._default_query.strip().lower()
        if feed not in self._ALLOWED_FEEDS:
            return False
        return True

    def health_check(self) -> bool:
        """Verify that the Hacker News API is reachable.

        Returns:
            True if a lightweight request to /maxitem.json succeeds;
            False on any network, API, or timeout error.
        """
        if not self.enabled:
            return False
        try:
            result = self._request("/maxitem.json")
            return isinstance(result, int)
        except (
            HackerNewsAPIError,
            TimeoutError,
            urllib.error.URLError,
            json.JSONDecodeError,
        ):
            return False


__all__ = [
    "HackerNewsProvider",
    "HackerNewsProviderError",
    "HackerNewsAPIError",
]
