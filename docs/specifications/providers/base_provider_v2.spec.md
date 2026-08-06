---
Title: Base Provider V2
Status: Draft
Version: 2.0
Owner: Founder
Reviewer: Chief Architect
Sprint: 2.2
Last Updated: 2026-08-03
---

# 1. Purpose

BaseProvider defines the mandatory contract that every provider implementation within Opportunity Intelligence Platform must follow.

It provides a stable abstraction between the Collector and external data sources.

No provider may bypass this contract.

---

# 2. Responsibilities

BaseProvider SHALL:

- Define provider identity
- Define provider metadata
- Define lifecycle interfaces
- Define validation rules
- Define health interface
- Define fetch interface

BaseProvider SHALL NOT:

- Execute scoring
- Normalize data
- Create Opportunity objects
- Perform business logic
- Interact with Dashboard
- Store provider instances

---

# 3. Provider Identity

Every provider MUST expose:

- id
- display_name

Requirements:

id

- unique
- immutable
- lowercase
- internal use only

display_name

- human readable
- UI friendly
- may change

Example

id = github

display_name = GitHub Trending

---

# 4. Provider Metadata

Every provider SHALL expose:

- description
- version
- category
- enabled
- timeout

Optional future metadata:

- author
- website
- documentation
- capabilities
- rate_limit
- priority

---

# 5. Required Interface

Every provider MUST implement:

fetch()

validate()

health_check()

metadata()

---

# 6. Fetch Contract

fetch()

Responsibilities:

- Connect to external service
- Retrieve raw data
- Return raw signals

Must NOT:

- Score
- Normalize
- Filter business logic
- Save files

---

# 7. Validation

validate()

Must verify:

- configuration
- required credentials
- required parameters

Must return validation status.

---

# 8. Health Check

health_check()

Must verify provider readiness.

Examples:

- API reachable
- Authentication valid
- Network available

Health checks must be lightweight.

---

# 9. Metadata Contract

metadata()

Returns provider information.

Minimum fields:

- id
- display_name
- description
- version
- category
- enabled
- timeout

---

# 10. Lifecycle

Provider Creation

↓

Validation

↓

Registration

↓

Fetch

↓

Shutdown

Future lifecycle events may be added without breaking existing providers.

---

# 11. Error Handling

Providers should raise provider-specific exceptions.

Common exceptions will be centralized in a future exceptions package.

---

# 12. Dependencies

BaseProvider depends on:

- Python Standard Library

BaseProvider must NOT depend on:

- Collector
- Registry
- Dashboard
- Intelligence
- Scoring
- Monitoring

---

# 13. Performance

Implementations should minimize memory usage.

Network operations should support configurable timeout values.

---

# 14. Security

Providers must never:

- expose secrets
- hardcode credentials
- read configuration files directly

Configuration must be injected externally.

---

# 15. Extensibility

Future provider implementations should require no modification of:

- Collector
- Registry
- Existing providers

Adding a provider should only require:

1. Implement BaseProvider

2. Register provider

---

# 16. Acceptance Criteria

Implementation is complete when:

- All abstract methods exist
- Type hints are complete
- Documentation is complete
- Unit tests pass
- Existing providers can inherit without architectural changes

---

# 17. Future Improvements

Planned enhancements:

- Async providers
- Provider capabilities
- Retry policy
- Provider state
- Metrics
- Telemetry
- Dependency Injection
- Plugin discovery
