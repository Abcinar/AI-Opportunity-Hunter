# ADR-0001 — Documentation Structure

**Status:** Accepted

**Date:** 2026-08-03

**Decision Makers:**
- Founder
- Chief Architect

---

# Context

The project is entering Phase 2 (Engineering Phase).

As the number of modules, providers and specifications grows, the documentation structure must remain scalable, discoverable and maintainable.

A clear separation of architectural concerns is required before implementation continues.

---

# Decision

The project documentation will be organized into dedicated domains.

```
docs/

    architecture/

    decisions/

    diagrams/

    specifications/

        providers/

        registry/

        collector/

        intelligence/

        scoring/

        dashboard/

        monitoring/

        testing/

        deployment/
```

Provider specifications belong under:

```
docs/specifications/providers/
```

Registry specifications belong under:

```
docs/specifications/registry/
```

---

# Rationale

Providers and Registry represent different architectural responsibilities.

Separating them improves:

- Single Responsibility
- Discoverability
- Scalability
- Maintainability

---

# Consequences

Future specifications will follow the same domain-based organization.

All engineering documentation must be placed inside the appropriate domain folder.

New architectural decisions will be recorded as ADR documents.

---

# Status

Accepted

Phase 2 Official Architecture
