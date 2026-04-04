## Context

The platform currently supports sync records for source-post batches, content-draft batches, and publish jobs, with safe and live-shell Feishu provider selection.

## Goals / Non-Goals

**Goals:**
- Formalize sync-record persistence and sync-provider selection.
- Preserve generation-stage and publish-stage sync behavior.

**Non-Goals:**
- Full Feishu Bitable schema mapping
- Real external upsert guarantees in phase one

## Decisions

### Decision: Sync happens at batch and publish boundaries

The platform SHALL sync source-post batches, content-draft batches, and publish jobs as separate sync record types.

### Decision: Sync providers mirror the safe/live provider pattern

The sync layer SHALL support safe stubs and live shells under configuration.

## Risks / Trade-offs

- [Real Feishu mapping is not fully validated] → Keep batch-level sync semantics and safe fallback in place.

## Migration Plan

1. Preserve current sync-record types.
2. Deepen real Feishu mapping later without changing sync-record semantics.

## Open Questions

- Which Bitable schema layout should be considered canonical first?
