"Bu doküman, AI Opportunity Hunter Constitution v1.0'da tanımlanan ilkelerin teknik mimariye dönüştürülmesini tanımlar."
---

# SOURCE PROVIDER ABSTRACTION

## Vision

AI Opportunity Hunter shall never depend on a single data provider.

Every external platform is considered only a **Source Provider**.

The internal intelligence engine must never know:

- How data is collected
- Which protocol is used
- Whether the source uses API, RSS, HTML or GraphQL
- Authentication method
- Rate limiting strategy

These concerns belong exclusively to the Provider Layer.

---

## Provider Architecture

```
                    Internet
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
    GitHub          HackerNews      Product Hunt
        │               │                │
        ▼               ▼                ▼
 GitHubProvider   HackerNewsProvider ProductHuntProvider
        │               │                │
        └───────────────┼────────────────┘
                        ▼
               Provider Interface
                        ▼
                  Normalizer
                        ▼
                Intelligence Engine
                        ▼
                  Scoring Engine
                        ▼
              Recommendation Engine
                        ▼
                   Dashboard
```

---

# Provider Responsibilities

Each Provider is responsible for:

- Authentication
- Rate Limit Handling
- Retry Logic
- Error Recovery
- Data Collection
- Raw Data Validation
- Source Metadata
- Logging

Providers are NOT allowed to:

- Score opportunities
- Recommend ideas
- Apply business logic
- Calculate confidence
- Make investment decisions

Those responsibilities belong to the Intelligence Layer.

---

# Provider Contract

Every provider must return exactly the same normalized structure.

Example:

```python
{
    "source": "github",
    "title": "...",
    "summary": "...",
    "url": "...",
    "created_at": "...",
    "engagement": 0,
    "category": "...",
    "language": "...",
    "metadata": {}
}
```

No provider may introduce provider-specific fields into the intelligence engine.

---

# Supported Provider Types

Current Providers

- GitHub Trending
- Hacker News
- Google Trends

Planned Providers

- Product Hunt
- Hugging Face
- Dev.to
- Stack Overflow
- PyPI
- npm Registry
- GitLab Trending
- Arxiv
- Papers With Code

Future Providers

- Reddit
- X (Twitter)
- YouTube
- Indie Hackers
- Crunchbase
- G2
- Capterra

---

# Design Principles

The Provider Layer follows these engineering principles.

## Open for Extension

New providers should be added without modifying existing providers.

## Closed for Modification

Existing providers should remain stable.

## Fault Isolation

Failure of one provider must never stop the entire pipeline.

## Replaceability

Any provider can be replaced without affecting the Intelligence Engine.

## Technology Independence

The Intelligence Engine must never know whether data came from:

- REST API
- GraphQL
- RSS Feed
- HTML Parser
- CSV
- JSON
- Database
- Local Cache

---

# Long-Term Goal

The Provider Layer is designed as a plug-in architecture.

Adding a new provider should require only:

1. Create Provider
2. Register Provider
3. Run Collector

No other module should require modification.

---

> Architecture Principle

"Data sources are replaceable.
Knowledge is permanent."
---

# PROVIDER LIFECYCLE

## Overview

Every provider follows exactly the same lifecycle.

No provider may skip any stage.

```
Initialize
      │
      ▼
Authenticate
      │
      ▼
Check Rate Limits
      │
      ▼
Collect Raw Data
      │
      ▼
Validate Response
      │
      ▼
Normalize Data
      │
      ▼
Attach Metadata
      │
      ▼
Return Opportunities
      │
      ▼
Shutdown
```

---

## Stage 1 — Initialization

Responsibilities

- Load configuration
- Validate credentials
- Prepare HTTP session
- Initialize logger

Output

Provider is ready.

---

## Stage 2 — Authentication

Supported methods

- API Key
- OAuth2
- Client Credentials
- Anonymous Access
- RSS
- Public HTML

Authentication must be isolated inside the provider.

---

## Stage 3 — Rate Limit Protection

Each provider must protect itself against:

- HTTP 429
- Temporary bans
- Connection limits
- Daily quotas

Strategies

- Exponential Backoff
- Retry Queue
- Sleep Strategy
- Circuit Breaker

---

## Stage 4 — Data Collection

Responsibilities

- Download data
- Handle pagination
- Handle network failures
- Retry transient errors

Raw data must never reach the Intelligence Engine.

---

## Stage 5 — Validation

Every record must be validated.

Required fields

- title
- url
- source

Optional fields

- engagement
- summary
- category
- language
- metadata

Invalid records are discarded.

---

## Stage 6 — Normalization

All providers produce identical output.

No provider-specific schema is allowed.

Normalization is mandatory.

---

## Stage 7 — Metadata

Metadata examples

- collected_at
- provider_version
- response_time
- retries
- source_region

Metadata never affects scoring.

---

## Stage 8 — Return

The provider returns

List[Opportunity]

Nothing else.

---

## Failure Policy

If a provider fails

↓

Log Error

↓

Retry

↓

Return Empty List

↓

Continue Pipeline

System availability is more important than provider availability.

---

## Engineering Rule

A provider may fail.

The platform must never fail.
