## Why

The platform requires explicit domain entities and lifecycle rules so workflow behavior remains consistent across REST, MCP, and Web entrypoints.

## What Changes

- Add core entities and value objects.
- Add draft and publish job state machines.
- Define transition rules and validation boundaries.

## Capabilities

### New Capabilities

- `core-domain-models`: Shared entities for content, publishing, and sync flows.
- `state-transition-rules`: Validated draft and publish transitions.

### Modified Capabilities

None.

## Impact

- Affects every business-facing workflow and test strategy.
