## Context

The project now exposes a working REST API for pipeline runs, draft review, publishing, sync records, audit logs, provider diagnostics, and observability summaries. The canonical `rest-api` change needs to formalize those interface guarantees so future providers and workflow features extend the same contract.

## Goals / Non-Goals

**Goals:**
- Define the shared REST surface over the application service layer.
- Keep auth, validation, and observability consistent across endpoints.
- Preserve the current endpoints for runs, drafts, publish jobs, sync records, audit logs, and diagnostics.

**Non-Goals:**
- Public multi-tenant API governance
- Versioned external API stability guarantees

## Decisions

### Decision: REST stays thin over shared services

Routes SHALL delegate to shared application services and not embed workflow logic.

### Decision: Auth is header-based for operator APIs

When auth is enabled, REST SHALL require the operator key header for protected endpoints.

### Decision: Diagnostics are first-class endpoints

The API SHALL expose run diagnostics, provider diagnostics, and observability summaries explicitly rather than hiding them in logs only.

## Risks / Trade-offs

- [Route surface grows quickly] → Keep all route behavior backed by shared services and schemas.
- [Auth is currently coarse] → Accept a single-team operator-key model in phase one and evolve later.

## Migration Plan

1. Preserve the current route structure.
2. Add more entity-specific endpoints only through the same service layer.

## Open Questions

- When public API versioning becomes necessary, should it use path prefixes or headers?
