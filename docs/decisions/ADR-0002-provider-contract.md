# ADR-0002

# Provider Contract

- Status: Accepted
- Date: 2026-08-03
- Decision Makers:
  - Founder
  - Chief Architect

---

# Context

Opportunity Intelligence Platform collects opportunity signals from multiple external sources.

Examples include:

- GitHub
- Hacker News
- Reddit
- Google Trends
- Product Hunt
- Future providers

The project requires a stable and extensible contract that every provider must implement.

The architecture must support adding new providers without modifying existing code.

This follows the Open/Closed Principle.

---

# Decision

Every provider SHALL inherit from BaseProvider.

BaseProvider represents the provider contract.

The contract defines:

- Identity
- Metadata
- Lifecycle
- Fetch interface
- Validation interface
- Health interface

No provider may bypass this contract.

---

# Provider Identity

Every provider SHALL expose a unique identifier.

Example

github

reddit

google

hackernews

producthunt

The identifier MUST remain stable.

It is used internally by:

- Registry
- Collector
- Configuration
- Logging

The identifier MUST NOT change because of UI requirements.

---

# Display Name

Every provider SHALL expose a human-readable display name.

Examples

GitHub Trending

Google Trends

Reddit

Hacker News

Display names may change.

Internal identifiers may not.

---

# Metadata

Every provider SHALL expose metadata.

Minimum metadata:

- id
- display_name
- description
- version
- category
- enabled
- timeout

Future versions may extend this list.

---

# Responsibilities

Providers SHALL:

- Connect to external systems
- Retrieve raw data
- Validate their configuration
- Report health status

Providers SHALL NOT:

- Score opportunities
- Normalize data
- Generate Opportunity objects
- Execute business logic
- Perform dashboard operations

---

# Data Flow

External API

↓

Provider

↓

Raw Signal

↓

Normalizer

↓

Opportunity

↓

Scoring Engine

↓

Dashboard

---

# Registration

Providers are registered inside Provider Registry.

Providers are never instantiated by the registry.

The registry stores provider instances only.

---

# Lifecycle

Provider Creation

↓

Validation

↓

Registration

↓

Fetch

↓

Shutdown

Future versions may introduce additional lifecycle states.

---

# Error Handling

Providers should raise provider-specific exceptions.

Common exception types will be introduced in a dedicated exceptions package.

---

# Health Check

Every provider SHALL expose a health check interface.

Health checks must not execute business logic.

Health checks only verify provider readiness.

---

# Configuration

Providers shall receive configuration from the configuration layer.

Providers must never read configuration files directly.

---

# Dependency Direction

Collector

↓

Provider Registry

↓

Provider Contract

↓

Provider Implementation

No dependency may point upward.

---

# Extensibility

New providers must be addable without modifying:

- Collector
- Registry
- Existing providers

The only required work should be:

1. Create provider
2. Register provider

No additional architectural changes should be necessary.

---

# Consequences

Benefits

- Strong architecture
- Open/Closed compliance
- Easier testing
- Easier plugin support
- Cleaner separation of concerns
- Lower technical debt

Trade-offs

- Slightly more initial design work
- More abstract architecture

These trade-offs are accepted.

---

# Status

Accepted

Sprint 2.2

Phase 2 Engineering
