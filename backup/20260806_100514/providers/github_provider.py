"""GitHub Provider V2 for AI Opportunity Hunter.

Concrete implementation of BaseProvider that retrieves raw opportunity
signals from the official GitHub REST API. Returns unprocessed JSON only.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from providers.base_provider import BaseProvider


class GitHubProviderError(Exception):
    """Base exception for all GitHubProvider failures."""


class GitHubAuthenticationError(GitHubProviderError):
    """Raised when GitHub authentication fails or the token is invalid."""


class GitHubRateLimitError(GitHubProviderError):
    """Raised when the GitHub API rate limit has been exceeded."""

    def __init__(self, message: str, reset_at: int | None = None) -> None:
        super().__init__(message)
        self.reset_at = reset_at


class GitHubAPIError(GitHubProviderError):
    """Raised for non-rate-limit, non-auth GitHub API errors."""


class GitHubProvider(BaseProvider):
    """Provider that fetches raw data from the GitHub REST API.

    Configuration and secrets are injected at construction time.
    The provider never normalizes, scores, or scrapes HTML.
    """

    _API_BASE = "https://api.github.com"
    _ACCEPT_HEADER = "application/vnd.github+json"
    _API_VERSION = "2022-11-28"

    def __init__(
        self,
        token: str,
        *,
        enabled: bool = True,
        timeout: float = 30.0,
        default_query: str = "AI OR LLM OR \"machine learning\"",
        per_page: int = 30,
        sort: str = "stars",
        order: str = "desc",
    ) -> None:
        """Initialize the GitHub provider.

        Args:
            token: GitHub personal access token or installation token.
            enabled: Whether the provider is active.
            timeout: Request timeout in seconds.
            default_query: Default search query used by fetch().
            per_page: Number of results per page (max 100).
            sort: Sort field for search results.
            order: Sort order (\"asc\" or \"desc\").
        """
        super().__init__(
            id="github",
            display_name="GitHub",
            description="Raw opportunity signals from GitHub REST API",
            version="2.0.0",
            category="code",
            enabled=enabled,
            timeout=timeout,
            capabilities=["repository_search", "issue_search", "repo_details"],
        )
        self._token = token
        self._default_query = default_query
        self._per_page = min(max(per_page, 1), 100)
        self._sort = sort
        self._order = order

    def _build_headers(self) -> dict[str, str]:
        """Build the standard request headers including authentication."""
        return {
            "Accept": self._ACCEPT_HEADER,
            "Authorization": f"Bearer {self._token}",
            "X-GitHub-Api-Version": self._API_VERSION,
            "User-Agent": "AI-Opportunity-Hunter/2.0",
        }

    def _request(self, path: str, params: dict[str, str] | None = None) -> Any:
        """Execute a GET request against the GitHub REST API.

        Args:
            path: API path beginning with '/'.
            params: Optional query parameters.

        Returns:
            Parsed JSON response body.

        Raises:
            GitHubAuthenticationError: On 401 or 403 authentication failures.
            GitHubRateLimitError: When rate limit is exceeded.
            GitHubAPIError: For other non-success status codes.
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
                remaining = response.headers.get("X-RateLimit-Remaining")
                if remaining is not None and int(remaining) == 0:
                    reset = response.headers.get("X-RateLimit-Reset")
                    reset_at = int(reset) if reset is not None else None
                    raise GitHubRateLimitError(
                        "GitHub API rate limit exceeded",
                        reset_at=reset_at,
                    )
                return json.loads(body)
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                remaining = (
                    exc.headers.get("X-RateLimit-Remaining") if exc.headers else None
                )
                if remaining is not None and int(remaining) == 0:
                    reset = exc.headers.get("X-RateLimit-Reset")
                    reset_at = int(reset) if reset is not None else None
                    raise GitHubRateLimitError(
                        "GitHub API rate limit exceeded",
                        reset_at=reset_at,
                    ) from exc
                raise GitHubAuthenticationError(
                    f"GitHub authentication failed (HTTP {exc.code})"
                ) from exc
            raise GitHubAPIError(
                f"GitHub API error (HTTP {exc.code}): {exc.reason}"
            ) from exc
        except TimeoutError as exc:
            raise TimeoutError(
                f"GitHub request timed out after {self.timeout}s"
            ) from exc
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, TimeoutError):
                raise TimeoutError(
                    f"GitHub request timed out after {self.timeout}s"
                ) from exc
            raise

    def fetch(self) -> Any:
        """Retrieve raw repository search results from GitHub.

        Returns:
            The unprocessed JSON payload returned by the GitHub
            /search/repositories endpoint.

        Raises:
            RuntimeError: If the provider is disabled.
            GitHubAuthenticationError: When the token is rejected.
            GitHubRateLimitError: When the rate limit is exceeded.
            GitHubAPIError: For other API errors.
            TimeoutError: When the request times out.
        """
        if not self.enabled:
            raise RuntimeError("GitHubProvider is disabled")

        params = {
            "q": self._default_query,
            "sort": self._sort,
            "order": self._order,
            "per_page": str(self._per_page),
        }
        return self._request("/search/repositories", params=params)

    def validate(self) -> bool:
        """Validate provider configuration and readiness.

        Returns:
            True if the provider is enabled, the token is present,
            and configuration values are valid; False otherwise.
        """
        if not self.enabled:
            return False
        if not self._token or not self._token.strip():
            return False
        if not self._default_query or not self._default_query.strip():
            return False
        if self.timeout <= 0:
            return False
        if self._per_page < 1 or self._per_page > 100:
            return False
        if not self._sort or not self._sort.strip():
            return False
        if self._order not in ("asc", "desc"):
            return False
        return True

    def health_check(self) -> bool:
        """Verify that the GitHub API is reachable and the token is accepted.

        Returns:
            True if a lightweight request succeeds; False on any
            network, authentication, rate-limit, or API error.
        """
        if not self.enabled or not self._token:
            return False
        try:
            self._request("/rate_limit")
            return True
        except (
            GitHubAuthenticationError,
            GitHubRateLimitError,
            GitHubAPIError,
            TimeoutError,
            urllib.error.URLError,
            json.JSONDecodeError,
        ):
            return False


__all__ = [
    "GitHubProvider",
    "GitHubProviderError",
    "GitHubAuthenticationError",
    "GitHubRateLimitError",
    "GitHubAPIError",
]
