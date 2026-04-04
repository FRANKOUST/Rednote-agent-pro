## Why

The Xiaohongshu content platform needs a stable architectural foundation before crawler, generation, review, publish, and synchronization features can be implemented safely. Without a shared domain model, provider abstraction layer, and resumable job framework, later capabilities would duplicate logic across REST, MCP, and Web UI entrypoints and become hard to evolve.

## What Changes

- Create the modular monolith application skeleton for a single-team internal deployment.
- Add shared domain entities, state rules, and provider contracts for crawl, analysis, generation, review, publish, and sync workflows.
- Establish persistence, queue, configuration, and storage foundations used by all later changes.
- Add shared interface patterns so REST routes, MCP tools, and Web UI handlers call the same application services.
- Define the initial observability and validation conventions required for resumable stage-based jobs.

## Capabilities

### New Capabilities

- `platform-foundation`: Application bootstrap, configuration, persistence, queue wiring, and repository structure for the content platform.
- `workflow-orchestration`: Stage-based job orchestration, resumable execution checkpoints, and structured failure metadata.
- `provider-abstractions`: Contracts and adapter boundaries for LLM, image, publisher, and Feishu providers.
- `operator-entrypoints`: Shared service access patterns for REST, MCP, and Web UI interfaces.

### Modified Capabilities

None.

## Impact

- Affects backend app structure, database schema foundation, queue setup, storage conventions, and interface layering.
- Establishes the contract that later crawler, generation, publishing, and Feishu changes will implement against.
- Introduces dependencies on `FastAPI`, `SQLAlchemy`, `PostgreSQL`, `Celery`, `Redis`, and `Playwright`-compatible runtime support.
