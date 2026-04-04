## Context

The system exposes a lightweight JSON-RPC tool surface at `/mcp` that allows AI clients to list tools and call shared use cases such as pipeline runs and record listing.

## Goals / Non-Goals

**Goals:**
- Formalize MCP-style tool discovery and invocation over shared services.
- Keep auth and run semantics aligned with REST.

**Non-Goals:**
- Full production-grade MCP compatibility in phase one.

## Decisions

### Decision: Tool handlers reuse shared services

MCP tool calls SHALL invoke the same application services as REST and Web.

### Decision: MCP auth mirrors operator API auth

When auth is enabled, MCP SHALL require the same operator key header as REST.

## Risks / Trade-offs

- [Lightweight JSON-RPC surface may differ from stricter MCP clients] → Treat phase one as a shared-service-compatible bridge, then harden later.

## Migration Plan

1. Keep existing tools stable.
2. Add richer tool metadata and entities in later changes.

## Open Questions

- Which external MCP clients should define compatibility targets first?
