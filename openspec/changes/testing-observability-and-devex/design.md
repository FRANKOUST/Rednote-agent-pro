## Context

The project now has a local dev setup, `.env.example`, pytest coverage, request IDs, run diagnostics, provider diagnostics, audit logs, and portfolio/demo docs. The canonical change needs to capture those practices so future changes preserve them.

## Goals / Non-Goals

**Goals:**
- Define the current test baseline and local developer workflow.
- Formalize observability primitives such as request IDs, audit logs, run diagnostics, and provider diagnostics.
- Keep demo and portfolio docs in sync with the implemented behavior.

**Non-Goals:**
- Full CI/CD and production-grade monitoring stacks
- Distributed tracing backends

## Decisions

### Decision: Keep local setup low-friction

The platform SHALL remain runnable with local defaults and documented startup commands.

### Decision: Treat diagnostics as product features

Observability SHALL not be limited to stdout logs; run and provider diagnostics must remain queryable.

## Risks / Trade-offs

- [Observability can grow unevenly] → Keep summary endpoints and run diagnostics as explicit contracts.
- [Tests may become config-sensitive] → Preserve environment reset and import-isolation patterns in test setup.

## Migration Plan

1. Preserve local startup and test docs.
2. Expand diagnostics incrementally as more providers become real.

## Open Questions

- Which metrics should be exported first when a real monitoring backend is added?
