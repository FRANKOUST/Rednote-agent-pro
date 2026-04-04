# Progress

## 2026-04-04

- Audited the repository and confirmed it only contained planning artifacts, not runnable code.
- Initialized OpenSpec and created initial planning changes.
- Wrote platform design, roadmap, and bootstrap implementation plan documents.
- Completed OpenSpec artifacts for:
  - `bootstrap-xiaohongshu-content-platform`
  - `add-xiaohongshu-collector`
- Switched into autonomous delivery mode.
- Started canonical audit, operating docs, and implementation skeleton setup.

## Current Milestone

Deliver a runnable foundation with a mocked end-to-end pipeline, shared REST/MCP/Web entrypoints, persistence, review flow, publish audit trail, sync records, tests, and portfolio-ready docs.

## Milestone Achieved

- Added a runnable FastAPI application under `app/`
- Added SQLite-backed persistence models for workflow, content, publish, sync, and audit entities
- Added mock providers for collector, LLM, image, publisher, and sync
- Added configuration-driven provider registry
- Added inline and background dispatcher modes
- Added a shared `PipelineService` that runs the end-to-end demo workflow
- Added REST endpoints for runs, drafts, publish jobs, sync records, and audit logs
- Added MCP-style JSON-RPC tool surface
- Added Web Console with pipeline launch, approval, and publish actions
- Added README, `.env.example`, demo docs, showcase docs, audit docs, and blueprint docs
- Verified the project with `pytest -q` (`8 passed`)
- Completed full OpenSpec `design/specs/tasks` artifacts for:
  - `architecture-foundation`
  - `domain-model-and-state-machine`
  - `pipeline-orchestration`
- Added a safe Playwright-backed collector adapter with configuration-based selection and safe fallback behavior
- Added integration coverage proving the pipeline still completes when the collector is configured as `playwright`
- Added safe real-provider stubs and config-driven registry wiring for:
  - OpenAI-compatible LLM
  - OpenAI-compatible image generation
  - Xiaohongshu API publish
  - Xiaohongshu browser publish
  - Feishu sync
- Added operator auth baseline for REST and MCP through `X-Operator-Key`
- Added request-id middleware and observability summary endpoint
- Added pipeline run listing across REST, MCP, and Web Console
- Expanded the Web Console to show recent runs, publish jobs, and sync records
- Added persisted workflow stage diagnostics with provider-level visibility
- Added `/api/pipeline-runs/{id}/diagnostics` for per-run observability
- Added a `worker_stub` dispatcher mode as a transition step toward real external worker backends
- Refactored interface layers to build services per request, eliminating config-staleness from module-level singletons
- Added provider diagnostics for collector, model, image, publisher, and sync adapters
- Surfaced provider diagnostics in REST and the Web Console
- Added Web Console login flow and session-cookie auth for auth-enabled mode
- Kept operator auth consistent across REST, MCP, and Web surfaces
- Added live-provider adapter selection for OpenAI, Feishu, Xiaohongshu API publish, and browser publish
- Kept automatic fallback to safe stubs when credentials or runtime prerequisites are missing
- Deepened the OpenAI live adapters with real HTTP request shells and safe fallback behavior
- Promoted `httpx` to a runtime dependency for live-provider support
- Added real HTTP shells with fallback for Feishu live sync and Xiaohongshu API publish
- Deepened the Playwright collector into a real browser-navigation shell with automatic fallback
- Added a Playwright-based browser publish live shell with automatic safe fallback
- Synced source-post and content-draft batches into sync records during the main pipeline
- Added a live-publish safety gate that forces live providers back to safe stubs unless explicitly enabled
- Completed canonical OpenSpec `design/specs/tasks` artifacts for:
  - `rest-api`
  - `mcp-server`
  - `web-console`
  - `testing-observability-and-devex`
- Completed canonical OpenSpec `design/specs/tasks` artifacts for:
  - `portfolio-packaging`
  - `source-ingestion-and-analysis`
  - `draft-and-image-generation`
  - `review-workflow-and-audit`
  - `publishing-provider-system`
  - `feishu-sync`
- Added entity-level REST APIs for source posts, analysis reports, topic suggestions, and image assets
- Added matching MCP entity-query and detail tools
- Added an external worker adapter layer with subprocess and filesystem queue backends
- Added a Web Console entity view page
- Verified the project with `pytest -q` (`34 passed`)
- Completed canonical OpenSpec `design/specs/tasks` artifacts for:
  - `portfolio-packaging`
- Added entity-level REST APIs for source posts, analysis reports, topic suggestions, and image assets
- Added matching MCP entity-query tools for source posts, reports, topics, and image assets
- Added an external worker adapter layer with filesystem queue manifests and config wiring
- Added Web Console entity list and detail views for source posts and reports, plus entity summary views for topics and image assets
- Added provider health endpoint and surfaced provider health in the dashboard
- Verified the project with `pytest -q` (`40 passed`)
- Rewrote `README.md` into a detailed project guide covering architecture, runtime modes, APIs, MCP tools, auth, observability, testing, and extension paths
