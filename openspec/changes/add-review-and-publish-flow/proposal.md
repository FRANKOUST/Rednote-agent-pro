## Why

The platform must keep manual review as the default safety gate while still supporting configurable one-click publishing. Review and publish need their own change because they combine editorial workflow, provider routing, failure recovery, and operational auditability.

## What Changes

- Add review workflows for draft approval, rejection, and publish readiness.
- Add publish job creation and execution with API and browser automation providers.
- Support configuration-driven routing between publish providers and browser automation fallback.
- Persist publish records, execution logs, and retryable failure metadata.

## Capabilities

### New Capabilities

- `draft-review-workflow`: Manual review, rejection, approval, and publish-ready transitions for generated drafts.
- `publish-job-execution`: Publish job dispatch, provider routing, retries, and fallback handling.
- `publish-audit-trail`: Persistent publish attempt records, status transitions, and operator diagnostics.

### Modified Capabilities

None.

## Impact

- Affects workflow orchestration, provider abstractions, operator actions, and audit logging.
- Introduces the highest-risk operational path and requires clear failure classification and recovery behavior.
