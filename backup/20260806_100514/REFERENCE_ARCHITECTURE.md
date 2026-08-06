# Phase 2 Principle

We do not write code to make today's feature work.

We design systems that make tomorrow's features easy to build.

Every architectural decision must reduce future complexity.

Temporary speed must never create permanent technical debt.
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
---

# OPPORTUNITY PIPELINE

## Vision

Every opportunity travels through a deterministic processing pipeline.

Raw internet signals never become opportunities directly.

Every signal must pass through a sequence of engineering stages.

---

## Processing Pipeline

```
Internet
    │
    ▼
Providers
    │
    ▼
Collector
    │
    ▼
Normalizer
    │
    ▼
Deduplicator
    │
    ▼
Signal Analyzer
    │
    ▼
Intelligence Engine
    │
    ▼
Scoring Engine
    │
    ▼
Recommendation Engine
    │
    ▼
Knowledge Base
    │
    ▼
Dashboard
```

---

## Stage 1 — Providers

Mission

Collect raw information.

Examples

- GitHub
- Hacker News
- Google Trends
- Product Hunt
- Hugging Face

Output

Raw Signals

---

## Stage 2 — Collector

Mission

Merge all providers into one unified stream.

Responsibilities

- Scheduling
- Retry Logic
- Provider Management
- Source Monitoring

Output

Collected Signals

---

## Stage 3 — Normalizer

Mission

Convert every signal into a unified structure.

Responsibilities

- Rename fields
- Normalize timestamps
- Normalize language
- Normalize engagement metrics

Output

Normalized Opportunities

---

## Stage 4 — Deduplicator

Mission

Remove duplicated opportunities.

Detection methods

- URL similarity
- Title similarity
- Semantic similarity
- Hash comparison

Output

Unique Opportunities

---

## Stage 5 — Signal Analyzer

Mission

Extract intelligence from signals.

Examples

- Market pain
- Competition
- Trend strength
- Technology
- Founder fit

Output

Enriched Opportunity

---

## Stage 6 — Intelligence Engine

Mission

Think.

The Intelligence Engine never collects data.

It only reasons.

Responsibilities

- Pattern Recognition
- Opportunity Discovery
- Risk Detection
- Market Analysis

Output

Opportunity Intelligence

---

## Stage 7 — Scoring Engine

Mission

Score.

Inputs

- Trend
- Market
- Competition
- Timing
- Founder Fit
- Confidence

Output

Score

0 — 100

---

## Stage 8 — Recommendation Engine

Mission

Decide.

Possible decisions

- BUILD
- WATCH
- SKIP

No other decisions are allowed.

---

## Stage 9 — Knowledge Base

Mission

Remember.

The platform stores

- Previous Opportunities
- Previous Scores
- Historical Trends
- Learning Signals

The platform must improve over time.

---

## Stage 10 — Dashboard

Mission

Visualize.

The Dashboard never performs business logic.

It only presents intelligence.

---

# Engineering Principle

Each stage performs exactly one responsibility.

No stage may perform the responsibilities of another stage.

This separation guarantees maintainability,
scalability,
and replaceability.
---

# ENGINEERING LAWS

## Law 1 — Single Responsibility

Every module has exactly one responsibility.

Modules that perform multiple responsibilities must be split.

---

## Law 2 — Replaceability

Every component must be replaceable.

Changing one provider must never affect another provider.

---

## Law 3 — No Hidden Logic

Business logic must never exist inside:

- Dashboard
- Providers
- Configuration
- UI

Business logic belongs only to the Intelligence Layer.

---

## Law 4 — Stateless Providers

Providers never remember.

They only collect.

Memory belongs to the Knowledge Base.

---

## Law 5 — Data Before Decisions

No recommendation may be generated without evidence.

Every BUILD recommendation must be explainable.

Every SKIP recommendation must be explainable.

---

## Law 6 — Explainability

Every score must contain:

- Inputs
- Weights
- Reasoning
- Evidence

Black-box decisions are forbidden.

---

## Law 7 — Evidence First

Opinion is never accepted.

Evidence is mandatory.

Evidence sources include:

- GitHub
- Hacker News
- Google Trends
- Product Hunt
- Future Providers

---

## Law 8 — Provider Isolation

Providers never communicate with each other.

All communication happens through the Collector.

---

## Law 9 — Intelligence Isolation

The Intelligence Engine never knows:

- API Keys
- HTTP Requests
- Authentication
- HTML
- GraphQL
- RSS

It receives only normalized opportunities.

---

## Law 10 — Dashboard Purity

The Dashboard never performs calculations.

The Dashboard never makes recommendations.

The Dashboard visualizes only.

---

## Law 11 — Configuration First

Magic numbers are forbidden.

Every threshold must come from configuration.

---

## Law 12 — Fail Gracefully

Failure of one provider shall never stop:

- Collection
- Scoring
- Dashboard
- Recommendations

Partial intelligence is better than system failure.

---

## Law 13 — Observability

Every important action must be logged.

Every failure must be measurable.

Every provider must expose health information.

---

## Law 14 — Scalability

Adding a new provider must require:

- No Intelligence changes
- No Dashboard changes
- No Recommendation changes

Only registration.

---

## Law 15 — Testability

Every component must be testable independently.

Unit Tests

↓

Integration Tests

↓

Pipeline Tests

↓

Acceptance Tests

---

# Architecture Doctrine

Code follows Architecture.

Architecture follows Principles.

Principles follow Vision.

Vision never changes.
