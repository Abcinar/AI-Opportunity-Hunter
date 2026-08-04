# HackerNewsProvider V2 — Engineering Specification

## 1. Purpose

HackerNewsProvider V2 is a concrete implementation of `BaseProvider` responsible for retrieving raw opportunity signals from the official Hacker News API (Firebase-backed).  

Its sole purpose is to act as a thin, reliable data-access layer that returns unmodified Hacker News JSON payloads.  
It must not interpret, normalize, enrich, score, or transform the data in any way.

## 2. Responsibilities

- Inherit from `BaseProvider`.
- Accept all runtime configuration exclusively via an injected `ProviderConfig` instance.
- Fetch story ID lists from the official Hacker News feed endpoints (`topstories`, `newstories`, `beststories`, `askstories`, `showstories`, `jobstories`).
- Fetch individual item documents by ID.
- Return the raw JSON response bodies exactly as received from the API.
- Perform only structural validation required to confirm a successful HTTP response and well-formed JSON.
- Expose a health-check endpoint that verifies connectivity to the Hacker News API.
- Propagate failures according to the defined error-handling contract.
- Never scrape HTML, never access the file system, and never read environment variables.

## 3. Data Source

- **Base URL**: `https://hacker-news.firebaseio.com/v0/`
- **Protocol**: HTTPS only.
- **Primary Endpoints**:
  - Story ID lists:  
    - `/topstories.json`  
    - `/newstories.json`  
    - `/beststories.json`  
    - `/askstories.json`  
    - `/showstories.json`  
    - `/jobstories.json`
  - Individual items: `/item/{id}.json`
  - Max item ID (optional utility): `/maxitem.json`
- **Response Format**: Application/JSON (Firebase Realtime Database export).
- **Data Characteristics**: Public, read-only, near-real-time. No authentication required. No official rate limit stated.

## 4. Authentication

- None required.
- The official Hacker News API is completely public and unauthenticated.
- No API keys, tokens, or credentials may be accepted, stored, or transmitted.
- ProviderConfig may contain authentication fields for compatibility across providers. HackerNewsProvider MUST ignore those fields because the official Hacker News API requires no authentication.

## 5. Provider Metadata

| Field              | Value                                      |
|--------------------|--------------------------------------------|
| | Field | Value |
|------|------|
| `id` | `"hackernews"` |
| `display_name` | `"Hacker News"` |
| `description` | `"Raw opportunity signals from Hacker News API"` |
| `version` | `"2.0.0"` |
| `category` | `"news"` |
| `enabled` | Injected (default `True`) |
| `timeout` | Injected |
| `capabilities` | `["topstories", "newstories", "beststories", "askstories", "showstories", "jobstories"]` |
| `max_items_per_fetch` | Configurable via `ProviderConfig` (default 30) |

Metadata must be exposed via the standard `BaseProvider` metadata interface.

## 6. Fetch Flow

1. Receive a fetch request containing an optional feed selector (default: `topstories`) and an optional `limit` (from `ProviderConfig` or request).
2. Construct the story-list URL: `{base_url}/{feed}.json`.
3. Perform an HTTP GET request with the configured timeout.
4. Parse the response as a JSON array of integer IDs.
5. Select the first `N` IDs according to the requested limit (IDs are already ranked by the API).
6. For each selected ID, perform an HTTP GET to `{base_url}/item/{id}.json`.
7. Collect the raw JSON objects (or `null` for deleted/missing items).
8. Return the list of raw JSON objects exactly as received.  
   No field mapping, type coercion, or filtering is permitted beyond discarding explicit `null` responses if configured.

Concurrent fetching of individual items is permitted provided the overall request remains within the timeout budget and does not violate polite usage.

## 7. Returned Raw Signal

The provider must return a list of raw Hacker News item objects.  
Each element is the exact JSON document returned by the `/item/{id}.json` endpoint, for example:

```json
{
  "by": "dhouston",
  "descendants": 71,
  "id": 8863,
  "kids": [8952, 9224, ...],
  "score": 111,
  "time": 1175714200,
  "title": "My YC app: Dropbox - Throw away your USB drive",
  "type": "story",
  "url": "http://www.getdropbox.com/u/2/screencast.html"
}
```

- No additional wrapper, metadata, or computed fields may be added by the provider.
- Deleted or non-existent items appear as JSON `null` and may be filtered only if the configuration explicitly requests it; otherwise they are returned as-is.

## 8. Validation

- HTTP status must be `200 OK`.
- Response body must be valid JSON.
- Story-list responses must be JSON arrays of integers.
- Item responses must be either a JSON object or JSON `null`.
- No semantic validation of HN-specific fields (score, time, type, etc.) is performed.
- Any validation failure raises a provider-specific exception that inherits from the base provider error hierarchy.

## 9. Health Check

- Endpoint: `GET https://hacker-news.firebaseio.com/v0/maxitem.json`
- Success criteria: HTTP 200 and a JSON number is returned.
- Must complete within the configured health-check timeout (default ≤ 5 s).
- Health-check result must be reported through the standard `BaseProvider` health interface without side effects.

## 10. Error Handling

| Condition                        | Behavior                                                                 |
|----------------------------------|--------------------------------------------------------------------------|
| Network / DNS failure            | Raise `ProviderConnectionError`                                          |
| HTTP status ≠ 200                | Raise `ProviderHTTPError` (include status code and body snippet)         |
| Invalid JSON                     | Raise `ProviderDataError`                                                |
| Timeout                          | Raise `ProviderTimeoutError`                                             |
| Empty story list                 | Return empty list (not an error)                                         |
| Individual item is `null`        | Include or skip according to configuration; never raise                  |
| Configuration missing required fields | Raise `ProviderConfigurationError` at construction time               |

All exceptions must carry sufficient context (URL, status, elapsed time) for observability while never logging or exposing secrets (none exist for this provider).

## 11. Rate Limits

- The official Hacker News API documents no hard rate limit.
- The provider must nevertheless implement polite throttling:
  - Configurable maximum concurrent item requests (default 10).
  - Configurable inter-request delay when sequential (default 0 ms, overridable via `ProviderConfig`).
- No client-side quota tracking beyond the concurrent-request limit is required.
- Operators are expected to respect community norms; the provider itself does not enforce external quotas.

## 12. Timeout

- Default request timeout: 10 seconds (configurable via `ProviderConfig`).
- Health-check timeout: 5 seconds (configurable).
- Overall fetch operation timeout: sum of story-list request + item-request budget, bounded by the configured global timeout.
- Timeouts must be enforced by the underlying HTTP client; the provider must not implement its own busy-wait timers.

## 13. Dependencies

- `BaseProvider` (abstract base class).
- `ProviderConfig` (injected configuration object).
- An HTTP client library capable of:
  - HTTPS GET requests
  - Configurable timeouts
  - Concurrent/async request support (recommended)
- JSON parser (standard library).
- No additional third-party Hacker News SDKs are permitted; only direct REST calls to the official Firebase endpoints.

## 14. Security

- No secrets are used or accepted.
- All communication occurs over HTTPS.
- No file-system access.
- No environment-variable access.
- No execution of untrusted content.
- Input validation is limited to ensuring feed names belong to the allowed set (`topstories`, `newstories`, `beststories`, `askstories`, `showstories`, `jobstories`) to prevent path injection.
- Provider must not log full response bodies at INFO level or higher; DEBUG logging of payloads is acceptable only when explicitly enabled via configuration.

## 15. Acceptance Criteria

1. Provider class inherits from `BaseProvider`.
2. Instantiation requires a `ProviderConfig` instance; no other configuration sources are used.
3. All network calls target only `https://hacker-news.firebaseio.com/v0/`.
4. No HTML parsing or scraping libraries appear in the dependency graph.
5. Returned data structures are identical to the raw JSON received from the API (byte-for-byte after JSON round-trip).
6. No scoring, ranking, or normalization logic exists in the provider.
7. Health check succeeds against the live API and fails gracefully when the API is unreachable.
8. All error conditions listed in §10 raise the correct exception types.
9. Concurrent item fetching respects the configured concurrency limit.
10. Unit tests cover: successful fetch, empty feed, null items, timeouts, HTTP errors, and invalid JSON.
11. Integration test against the live public API (marked as optional/nightly) returns non-empty results for `topstories`.
12. Provider imports only BaseProvider and ProviderConfig from the provider layer and introduces no cross-layer dependencies.

## 16. Future Improvements

- Optional support for the Algolia HN Search API as a secondary, authenticated or higher-volume source (kept behind a feature flag and still returning raw JSON).
- Real-time listener mode using Firebase streaming (Server-Sent Events) for continuous signal ingestion.
- Configurable item-type filtering (`story`, `job`, `poll`) performed after raw retrieval, still without normalization.
- Built-in exponential back-off retry policy for transient network errors.
- Metrics emission (request latency, item count, error rate) through the standard observability interface.
- Support for fetching comment trees when explicitly requested, still returning the raw nested JSON structure.
