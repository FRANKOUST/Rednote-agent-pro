## Context

The platform now supports review approval, rejection, publish readiness, and audit-log capture across REST, MCP, and Web flows.

## Goals / Non-Goals

**Goals:**
- Formalize the review workflow and audit trail behavior.
- Preserve a clear distinction between draft review and publish execution.

**Non-Goals:**
- Multi-reviewer workflows
- Role-based audit filtering

## Decisions

### Decision: Audit records stay append-only

Audit logs SHALL record operator and system actions independently from the core business entities.

### Decision: Review stays explicit before publish

Approval SHALL remain a required transition before a draft can publish.

## Risks / Trade-offs

- [Single review state may be too simple later] → Extend from the current transition helper rather than bypassing it.

## Migration Plan

1. Keep audit-log and review transitions explicit.
2. Extend later with richer review states if needed.

## Open Questions

- Should reviewer identity become a first-class field once multi-user auth exists?
