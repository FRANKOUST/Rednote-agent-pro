## Why

The platform needs an external collaboration sink so generated and published artifacts can be shared outside the app.

## What Changes

- Add sync provider interface and default implementation.
- Add sync records tied to published entities.
- Prepare the path for Feishu Bitable integration.

## Capabilities

### New Capabilities

- `sync-provider-boundary`: Replaceable sync adapters.
- `sync-records`: Persistent record of external synchronization.

### Modified Capabilities

None.

## Impact

- Extends the platform into team collaboration workflows.
