## Why

The platform is intended to be operated by both humans and AI clients, so it needs stable operator surfaces beyond the internal service layer. REST APIs, MCP tools, and a practical web UI should be delivered together as a coherent operator-facing change over the already-stabilized workflow capabilities.

## What Changes

- Add operator-facing REST endpoints for crawl, analysis, generation, review, publish, and sync actions.
- Add MCP tools that expose the same use cases to Claude Desktop, Cursor, and similar clients.
- Add an internal web UI for launching jobs, viewing results, approving drafts, and tracking publish status.
- Standardize workflow status, validation, and error display across all three entrypoints.

## Capabilities

### New Capabilities

- `operator-rest-api`: Stable REST endpoints over shared platform use cases.
- `operator-mcp-tools`: MCP tools for AI-client access to platform workflows.
- `operator-web-console`: Human-oriented UI for managing crawl, generation, review, publish, and sync flows.

### Modified Capabilities

None.

## Impact

- Affects interface modules, shared schema definitions, and operator-facing observability.
- Requires consistent validation and status semantics across human and agent-facing interfaces.
