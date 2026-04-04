## Context

The project now contains a runnable FastAPI-based foundation, but the canonical OpenSpec change for that foundation has only a proposal. This design formalizes the intended shape of the architecture so later changes can depend on stable conventions instead of implementation accidents.

Current implementation uses:
- `FastAPI` for application bootstrap
- `pydantic-settings` for configuration
- `SQLAlchemy` for persistence
- server-rendered templates for the initial operator console
- a modular-monolith package layout under `app/`

The architecture must continue supporting:
- shared use-case services across REST, MCP, and Web
- a provider plugin layer for collector, LLM, image, publisher, and sync adapters
- local demo mode with low setup cost
- future migration toward PostgreSQL, Redis, Celery, and Playwright-backed integrations

## Goals / Non-Goals

**Goals:**
- Lock in the modular-monolith package boundaries and their responsibilities.
- Standardize bootstrapping, configuration loading, and local runtime conventions.
- Define a persistence foundation that is SQLite-friendly locally but PostgreSQL-compatible by design.
- Keep the interface layer thin and application-service driven.

**Non-Goals:**
- Implement real external providers or production deployment automation.
- Introduce multi-tenant authentication or SaaS concerns.
- Split the app into microservices.

## Decisions

### Decision: Keep a modular monolith

The system SHALL remain a modular monolith for phase one. All interfaces, providers, and domain rules live in one application process, but package boundaries remain explicit.

Alternatives considered:
- Microservices now: rejected because operational overhead is too high for the current stage.
- Single-file application: rejected because it undermines the provider and workflow abstractions needed for later phases.

### Decision: Support local SQLite-first runtime defaults

The local developer and demo environment SHALL default to SQLite and filesystem-backed media storage. This keeps startup friction low while preserving PostgreSQL-compatible schema conventions for later deployment.

Alternatives considered:
- PostgreSQL-only local setup: rejected because it creates unnecessary setup friction at the current stage.

### Decision: Route all operator surfaces through shared services

REST routes, MCP handlers, and Web Console actions SHALL invoke shared application services rather than embed workflow logic directly.

Alternatives considered:
- Per-interface logic forks: rejected because they would cause behavior drift and inconsistent validation.

### Decision: Keep provider lookups centralized

Provider selection SHALL live in a dedicated registry layer driven by configuration, not in individual routes or service branches.

Alternatives considered:
- Hardcoded provider construction in business logic: rejected because it blocks safe replacement with real providers later.

## Risks / Trade-offs

- [SQLite local defaults hide some PostgreSQL-specific behavior] → Keep persistence types simple and compatible; document the intended PostgreSQL migration path.
- [A modular monolith can drift into a tangled codebase] → Preserve file and package boundaries in the canonical architecture docs and change map.
- [Thin interfaces can be violated over time] → Keep acceptance criteria focused on shared service reuse.

## Migration Plan

1. Formalize architecture requirements in specs.
2. Keep local runtime defaults in place for the current implementation.
3. Expand follow-on changes behind the same package and service boundaries.

Rollback strategy:
- Revert new architecture-only documentation artifacts without touching implementation if the structure needs to be renegotiated.

## Open Questions

- When production deployment is introduced, should settings be split into explicit environment profiles or remain pure `.env`-driven?
- Will the first production background worker use Celery or a lighter queue abstraction adapter over the current dispatcher?
