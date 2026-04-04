## Context

The platform will be built as a single-team internal system that eventually supports Xiaohongshu crawling, analysis, topic generation, draft generation, image generation, review, publishing, Feishu sync, REST APIs, MCP tools, and a built-in web UI. This first change does not implement those business capabilities end to end. It creates the shared architecture required so later changes can add them without duplicating state rules, provider wiring, or interface logic.

Current repository state is an empty workspace with initialized OpenSpec metadata only. That means this change must define both the repository skeleton and the operational contracts for later phases.

Constraints:
- Manual review remains the default publishing gate at the product level.
- REST, MCP, and Web UI must share the same application layer.
- External systems such as OpenAI, Feishu, and Xiaohongshu publishing endpoints must be isolated behind adapters.
- Long-running work must run asynchronously with durable stage checkpoints.

## Goals / Non-Goals

**Goals:**
- Establish a modular monolith structure for backend interfaces, application services, domain rules, and infrastructure adapters.
- Define canonical domain entities and state models for later pipeline features.
- Add persistence and queue foundations for resumable stage-based jobs.
- Create provider contracts for LLM, image, publisher, and Feishu integrations.
- Make REST, MCP, and Web UI entrypoints call shared use-case services instead of owning business logic.

**Non-Goals:**
- Implement the crawler, analyzer, topic generator, draft generator, publish adapters, or Feishu sync behavior in full.
- Build a complete authentication system or multi-tenant access model.
- Optimize for internet-scale throughput in the first iteration.
- Deliver a polished production UI beyond a thin operational shell.

## Decisions

### Decision: Use a modular monolith instead of microservices

The first release SHALL use a single `FastAPI` application with strict internal boundaries. This keeps deployment and iteration simple while preserving clear module seams for future extraction.

Alternatives considered:
- Microservices now: rejected because the team would pay orchestration and deployment overhead before business behavior is proven.
- Workflow engine first: rejected because the abstraction level is too high for the empty starting point.

### Decision: Use stage-based async jobs with durable checkpoints

Long-running actions SHALL execute in queue-backed jobs and persist stage outputs or status snapshots after each stage. This enables retries from the failed stage rather than rerunning the entire pipeline.

Alternatives considered:
- Synchronous HTTP request execution: rejected due to timeout risk and poor operator visibility.
- Fire-and-forget jobs without checkpoints: rejected because failures would be opaque and expensive to recover from.

### Decision: Use provider interfaces for all external systems

The design SHALL define contracts for LLM, image, publisher, and Feishu integrations before implementing specific vendors. OpenAI is the initial provider, but the application layer must not depend on vendor-specific SDK shapes.

Alternatives considered:
- Direct OpenAI-only integration: rejected because vendor lock-in would spread into core business code.
- Generic tool execution abstraction for everything: rejected because it would obscure domain-specific error handling.

### Decision: Keep interface layers thin and shared-service driven

REST routes, MCP tools, and Web UI handlers SHALL be adapters over the same application services and DTOs. Any business rule added later must live in application or domain code.

Alternatives considered:
- Separate controllers and per-entrypoint service logic: rejected because it would create divergence between human and agent interfaces.

### Decision: Separate content review state from publish execution state

`ContentDraft` approval and `PublishJob` execution SHALL remain different state machines. A draft can be approved without being published, and a publish attempt can fail without invalidating the approved draft.

Alternatives considered:
- Single combined lifecycle: rejected because it would couple editorial decisions to operational failures.

## Risks / Trade-offs

- [Initial abstraction overhead] → Keep the first change limited to contracts, skeletons, and shared foundations; defer feature-specific complexity to later changes.
- [Queue and database setup increases local complexity] → Provide a minimal local development stack and keep infrastructure choices conventional.
- [Provider contracts may be too generic] → Shape contracts around domain use cases such as draft generation and publish execution rather than raw SDK calls.
- [Empty-repo planning can drift from implementation reality] → Use follow-on OpenSpec changes with focused capability specs before each subsystem is implemented.

## Migration Plan

1. Create the repository skeleton, dependency manifests, and application bootstrap.
2. Add configuration, persistence, queue wiring, and storage abstractions.
3. Add domain models and provider contracts.
4. Add shared application services and placeholder entrypoints for REST, MCP, and Web UI.
5. Validate the structure with automated tests and OpenSpec validation before starting feature-specific changes.

Rollback strategy:
- Because the repository is currently empty, rollback for this initial change is equivalent to reverting the newly created foundation files before any downstream changes depend on them.

## Open Questions

- Which local development environment will be standardized for Playwright browser state and Xiaohongshu login persistence?
- Will the thin Web UI be server-rendered with templates or a separate lightweight frontend package?
- Which job backend configuration should be default for development: Redis-only local setup or containerized Postgres plus Redis from day one?
