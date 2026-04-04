## Context

The current implementation has concrete persistence tables, in-memory payload models, and explicit state transitions for drafts and publish jobs. The canonical change needs to formalize those rules so future features such as richer review flows, retries, and real providers extend the same model instead of creating parallel interpretations.

The domain currently includes:
- source content snapshots
- analysis reports and topic suggestions
- generated drafts and image assets
- publish job records
- sync records
- audit logs

## Goals / Non-Goals

**Goals:**
- Formalize the core domain entities required by the product boundary.
- Lock in the draft and publish state transitions already used by the application service.
- Keep content lifecycle and publish lifecycle explicitly separate.

**Non-Goals:**
- Add complex approval hierarchies or multi-step publish rollback in this change.
- Model every future analytics or provider-specific attribute.

## Decisions

### Decision: Keep content and publish lifecycles separate

`ContentDraft` and `PublishJob` SHALL remain separate entities with separate lifecycle states.

Alternatives considered:
- Single combined content lifecycle: rejected because editorial approval and operational publish execution fail for different reasons.

### Decision: Use immutable-ish source evidence records

`SourcePost`, `AnalysisReport`, and `TopicSuggestion` SHALL act as evidence and generation inputs, not mutable latest-state records.

Alternatives considered:
- Mutable latest-state records: rejected because later review and audit tasks need traceability to original evidence.

### Decision: Express state transitions explicitly

Draft state changes SHALL happen through explicit transition rules rather than arbitrary direct assignment in multiple places.

Alternatives considered:
- Free-form status strings: rejected because they allow invalid state combinations and weaken tests.

## Risks / Trade-offs

- [The current state machine is intentionally small] → Expand later through controlled transition functions rather than ad hoc new statuses.
- [Persistence tables may need additional metadata] → Keep entity boundaries stable even if columns are added later.

## Migration Plan

1. Codify entity and state-machine requirements in specs.
2. Keep transition tests aligned with the explicit transition helper.
3. Extend entities in later changes without breaking the lifecycle split.

Rollback strategy:
- Revert documentation artifacts if the model must be renegotiated, while preserving the current tested implementation until a replacement exists.

## Open Questions

- Should future review flows introduce a dedicated `needs_revision` state, or stay within `rejected` plus notes?
- Should publish retries remain on `PublishJob` or be broken into child attempt records later?
