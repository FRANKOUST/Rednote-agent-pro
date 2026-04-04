## Why

The system is workflow-oriented, so it needs an explicit orchestration model instead of scattered function calls.

## What Changes

- Add workflow run records and staged execution.
- Add dispatcher abstraction for async execution.
- Add run status lookup and failure capture.

## Capabilities

### New Capabilities

- `workflow-runs`: Persisted pipeline execution records.
- `stage-orchestration`: Stage-based workflow execution and status tracking.

### Modified Capabilities

None.

## Impact

- Establishes the backbone for crawl, generate, publish, and sync flows.
