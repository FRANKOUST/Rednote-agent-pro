## Context

The current implementation runs an end-to-end workflow through a shared `PipelineService` and a dispatcher abstraction with `inline` and `background` modes. The orchestration change formalizes that behavior so later changes can swap in stronger queue backends without changing interface contracts.

The current workflow stages are:
- crawl
- analyze
- generate_topics
- generate_drafts
- generate_images
- review_gate
- publish
- sync_feishu

Today, generation runs are executed synchronously for the demo path, while dispatch mode controls whether task invocation is immediate or background-threaded.

## Goals / Non-Goals

**Goals:**
- Define persisted workflow-run records and stage tracking.
- Define dispatcher behavior as an internal abstraction over execution mode.
- Preserve the contract that operator entrypoints create trackable workflow records and later query them.

**Non-Goals:**
- Introduce a production-grade queue backend in this change.
- Model every future retry or resume nuance.

## Decisions

### Decision: Keep a dispatcher abstraction in front of execution

The application SHALL use a dispatcher abstraction that can run tasks inline for local mode or asynchronously for background mode.

Alternatives considered:
- Hardcode inline execution: rejected because it blocks evolution toward queue-backed execution.
- Introduce Celery immediately: rejected because the current project benefits more from a stable abstraction and low-friction local execution.

### Decision: Persist workflow-run records independently of execution mode

Workflow runs SHALL be persisted whether they execute inline or in background mode so operator surfaces can query status consistently.

Alternatives considered:
- In-memory workflow status only: rejected because it breaks auditability and multi-surface access.

### Decision: Keep stage transitions explicit in the workflow record

The workflow run SHALL store its current stage and status so failures and dashboards can reason about progress.

Alternatives considered:
- Store only final result summaries: rejected because it weakens observability and failure diagnosis.

## Risks / Trade-offs

- [Background thread mode is not a production worker system] → Treat it as an evolution step, not the final queue backend.
- [Inline execution returns fully computed results too quickly for some workflows] → Preserve run records and interface contracts so real async replacement stays possible.

## Migration Plan

1. Formalize workflow-run and dispatcher requirements in specs.
2. Keep the existing inline/background dispatcher implementation as the reference behavior.
3. Replace the dispatcher backend later without changing route contracts.

Rollback strategy:
- Revert orchestration-only docs if needed while leaving the current tested service behavior intact until a better orchestration layer exists.

## Open Questions

- Should the first real queue backend be Celery or an adapter over a lighter in-process queue?
- When resume and retry semantics are added, should each stage write checkpoint payloads or stage-attempt records?
