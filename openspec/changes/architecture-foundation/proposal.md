## Why

The project needs a stable modular-monolith foundation before any domain workflow can be implemented safely. Without shared app bootstrap, persistence, configuration, and interface boundaries, later changes would duplicate logic and become hard to evolve.

## What Changes

- Add application bootstrap and module structure.
- Add configuration loading and environment conventions.
- Add persistence base and local runtime defaults.
- Add shared service layering for REST, MCP, and Web UI.

## Capabilities

### New Capabilities

- `platform-bootstrap`: App startup, configuration, and runtime conventions.
- `module-boundaries`: Interface, application, domain, and infrastructure separation.

### Modified Capabilities

None.

## Impact

- Affects all later changes.
- Establishes the technical foundation for local demo and future production deployment.
