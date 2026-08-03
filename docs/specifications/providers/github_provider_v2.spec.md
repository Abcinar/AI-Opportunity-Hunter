- If the token is missing, empty, or invalid, `validate()` MUST return `False` and `fetch()` MUST raise an authentication-related exception.

---

## 5. Provider Metadata

The following values are fixed for the GitHub Provider and are supplied to the `BaseProvider` constructor:

| Field          | Value                                      |
|----------------|--------------------------------------------|
| `id`           | `"github"`                                 |
| `display_name` | `"GitHub"`                                 |
| `description`  | `"Raw opportunity signals from GitHub REST API"` |
| `version`      | `"2.0.0"`                                  |
| `category`     | `"code"`                                   |
| `enabled`      | Injected (default `True`)                  |
| `timeout`      | Injected (default `30.0` seconds)          |
| `capabilities` | `["repository_search", "issue_search", "repo_details"]` |

These values are immutable after construction (enforced by BaseProvider V2 read-only properties).

---

## 6. Fetch Flow

1. Validate that the provider is enabled and correctly configured.
2. Build the request URL and query parameters from the injected configuration (search query, sort, order, per_page, page, etc.).
3. Issue an HTTP GET request to the GitHub REST API with the required headers and the configured timeout.
4. If the response status is 2xx, return the parsed JSON body (or the full response object if the configuration requests it) as raw data.
5. If the response indicates rate limiting (HTTP 403 with rate-limit headers) or any other error, raise a dedicated exception containing the status code and message.
6. Never retry automatically inside `fetch()`; retry policy belongs to the Collector or a higher-level orchestrator.

---

## 7. Returned Raw Signal

`fetch()` MUST return the unprocessed JSON payload received from GitHub.

Typical shapes:

- Search results: `{"total_count": int, "incomplete_results": bool, "items": [...]}`
- Single repository: the full repository object
- Issues / Pull Requests: list of issue/PR objects

No fields are added, removed, or renamed.  
The Normalizer layer is solely responsible for mapping this raw signal into the internal Opportunity schema.

---

## 8. Validation

`validate() -> bool` MUST perform the following checks:

- Provider is enabled.
- Authentication token is present and non-empty.
- Required configuration keys (base URL, default query, timeout) are present and of correct type.
- Timeout value is positive.

Returns `True` only when all checks pass; otherwise returns `False`.  
It MUST NOT raise for ordinary configuration problems; it only raises for unexpected internal errors.

---

## 9. Health Check

`health_check() -> bool` MUST:

- Issue a lightweight request (recommended: `GET /rate_limit` or `GET /zen`).
- Return `True` if the response is 2xx and the API is reachable.
- Return `False` for network errors, timeouts, authentication failures, or non-2xx responses.
- Never raise for ordinary unavailability; only raise for unexpected internal errors that prevent the check itself from running.

---

## 10. Error Handling

- All network, HTTP, and JSON-decoding errors MUST be wrapped in provider-specific exceptions (or standard exceptions with clear messages).
- Rate-limit responses (HTTP 403 + `X-RateLimit-Remaining: 0`) MUST raise a dedicated `GitHubRateLimitError` (or equivalent) that includes reset time when available.
- Authentication failures MUST raise an authentication-related exception.
- Silent failures are forbidden. Every failure path must either return `False` (for `validate` / `health_check`) or raise.

---

## 11. Rate Limits

- The provider MUST read and respect the standard GitHub rate-limit headers:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`
- When remaining requests reach zero, further calls to `fetch()` MUST raise a rate-limit exception instead of issuing the request.
- The provider itself does not implement sleeping or token-bucket logic; that responsibility lies with the calling orchestrator.

---

## 12. Timeout

- Every HTTP request MUST be executed with the timeout value supplied at construction (default 30 seconds).
- Both connect and read timeouts are covered by the single value.
- On timeout, `fetch()` and `health_check()` MUST surface a timeout exception (or return `False` for health_check).

---

## 13. Dependencies

**Allowed:**

- Python 3.12 standard library
- `httpx` or `urllib3` / `requests` (only for HTTP transport)
- `BaseProvider` from `providers.base_provider`

**Forbidden:**

- Collector
- ProviderRegistry
- Dashboard
- Scoring
- Intelligence
- Any HTML parsing libraries (BeautifulSoup, lxml, etc.)
- Any AI / LLM libraries

---

## 14. Security

- Secrets (tokens) are injected and stored only in private attributes.
- Tokens MUST never appear in logs, exception messages, or returned data.
- All communication MUST use HTTPS.
- No credentials are written to disk by the provider.
- Input configuration is treated as untrusted; query parameters are properly encoded.

---

## 15. Acceptance Criteria

- [ ] Class inherits from `BaseProvider` and is not instantiable without implementing the abstract methods.
- [ ] All metadata properties return the values defined in section 5.
- [ ] `fetch()` returns raw GitHub JSON without modification.
- [ ] `validate()` returns `bool` and correctly detects missing token / invalid config.
- [ ] `health_check()` returns `bool` and correctly reports API reachability.
- [ ] No HTML scraping code exists.
- [ ] No scoring, normalization, or cross-layer imports exist.
- [ ] Secrets are never hardcoded.
- [ ] Rate-limit headers are inspected.
- [ ] Configured timeout is applied to every request.
- [ ] All public methods have complete Google-style docstrings and full type hints.
- [ ] Code is PEP-8 compliant and contains no placeholders, TODOs, or dead code.

---

## 16. Future Improvements

- Optional support for GitHub GraphQL API (behind a capability flag).
- Fine-grained permission introspection for GitHub App tokens.
- Built-in pagination helper that still returns raw pages (no aggregation).
- Metrics hooks (request count, latency) that remain optional and side-effect free.
- Support for GitHub Enterprise Server base URLs via configuration.

These items are out of scope for V2 and require a new specification revision before implementation.
