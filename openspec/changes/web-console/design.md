## Context

The project now includes a server-rendered Web Console with pipeline launch, draft review, publish actions, run lists, provider diagnostics, audit logs, publish records, sync records, and optional session login.

## Goals / Non-Goals

**Goals:**
- Formalize the Web Console as the human operator surface for phase one.
- Preserve a lightweight server-rendered design.
- Keep session login optional and only active when auth mode is enabled.

**Non-Goals:**
- Rich SPA behavior
- Fine-grained user management

## Decisions

### Decision: Server-rendered pages stay sufficient for phase one

The Web Console SHALL remain server-rendered and action-oriented for speed of development and low operational complexity.

### Decision: Auth-enabled mode uses session cookies

When auth is enabled, the console SHALL require operator login and session cookie access.

## Risks / Trade-offs

- [UI can become crowded] → Expand into more pages only when necessary.
- [Session auth is coarse] → Accept the shared-operator-key model for phase one.

## Migration Plan

1. Preserve the current login and dashboard flow.
2. Split pages later if the console grows beyond a single screen.

## Open Questions

- Which operator views should become separate pages first: runs, review queue, or diagnostics?
