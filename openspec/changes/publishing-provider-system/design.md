## Context

The platform now supports mock, safe-stub, and live-shell publish providers for API and browser modes, plus an explicit safety gate that forces live providers back to safe stubs unless live publishing is explicitly allowed.

## Goals / Non-Goals

**Goals:**
- Formalize the publish-provider abstraction and publish-job persistence.
- Keep live publish gated by configuration.

**Non-Goals:**
- Guaranteed production-safe browser automation
- Automatic rollback or takedown flows

## Decisions

### Decision: Live publish must be explicitly enabled

The system SHALL not execute live publish adapters unless an explicit live-publish feature flag is enabled.

### Decision: Publish jobs record actual executing provider

Publish job records SHALL store the provider that actually executed, including safe-stub fallbacks.

## Risks / Trade-offs

- [Live shells are not production validated] → Force explicit enablement and preserve safe fallback.

## Migration Plan

1. Keep current safe gate and provider recording.
2. Replace safe/live shells with validated integrations later.

## Open Questions

- Should live publish require an additional per-request confirmation token in the future?
