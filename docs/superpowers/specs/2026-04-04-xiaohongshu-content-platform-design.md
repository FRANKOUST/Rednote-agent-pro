# Xiaohongshu Content Platform Design

## Context

This project is a single-team internal platform for Xiaohongshu content mining, generation, review, and publishing. The product goal is a full loop from competitor data collection to publish-ready drafts, while keeping manual review as the default gate and one-click publishing as a configurable override.

The system must support:
- Xiaohongshu search crawling with result filtering and ad/video skipping
- Structured analysis of high-performing content
- Topic suggestion generation
- Draft generation with title, body, tags, CTA, image guidance, and content type
- Image generation through `gpt-image-1`, stored locally
- Publish through API mode or browser automation fallback
- Feishu Bitable synchronization for scraped and AI-generated records
- REST API, MCP tools, and a built-in web UI
- Pluggable model providers beyond OpenAI

## Scope

### In Scope

- Single-team internal deployment
- Shared domain services behind REST, MCP, and Web UI
- Provider abstraction for LLM, image, publishing, and Feishu integrations
- Stage-based asynchronous workflow with resumable checkpoints
- Auditability across crawl, generation, review, publish, and sync actions

### Out of Scope

- Multi-tenant SaaS, billing, and quota isolation
- Fine-grained enterprise RBAC
- Native mobile clients
- Production-grade anti-detection guarantees for crawler automation

## Architecture

The recommended architecture is a modular monolith built on `FastAPI`, with provider plugins and asynchronous job orchestration. `REST`, `MCP`, and `Web UI` are separate interface surfaces over the same application services.

### Layers

1. `interfaces`
   - REST routes
   - MCP tools
   - Web pages and lightweight frontend assets
2. `application`
   - Use-case services
   - Pipeline orchestration
   - Review and publish coordination
3. `domain`
   - Entities, value objects, state rules, provider contracts
4. `infrastructure`
   - Playwright crawler
   - LLM and image providers
   - Publish providers
   - Feishu adapters
   - Database, queue, storage

### Architectural Rules

- Interface code stays thin and never owns business rules.
- Long-running work goes through async jobs, not request threads.
- External systems are consumed only through provider contracts.
- Content review state and publish execution state are modeled separately.
- Historical crawl and analysis outputs are immutable snapshots.

## Core Domain Model

### Entities

- `SourcePost`: scraped competitor content snapshot with metrics and metadata
- `AnalysisReport`: structured summary of keyword, title, tag, and audience patterns
- `TopicSuggestion`: generated topic proposal with rationale and source references
- `ContentDraft`: AI-generated draft ready for review and later publishing
- `ImageAsset`: generated or uploaded media asset linked to a draft
- `PublishJob`: execution record for a publish attempt
- `SyncRecord`: outbound synchronization record for Feishu or future sinks

### Draft State Machine

`created -> generated -> review_pending -> approved | rejected -> publish_ready`

### Publish State Machine

`queued -> preparing -> publishing -> published | failed | cancelled`

## Workflow Design

The system uses stage-based orchestration with durable checkpoints:

1. `crawl`
2. `analyze`
3. `generate_topics`
4. `generate_drafts`
5. `generate_images`
6. `review_gate`
7. `publish`
8. `sync_feishu`

Each stage writes a clear output artifact to storage. Downstream stages consume persisted outputs instead of in-memory data from the previous step. Failures are classified by stage and marked as retryable or non-retryable with structured diagnostics.

## Product and Platform Rules

### Review and Publish

- Manual review is required by default.
- One-click publish is a configurable override at system or job scope.
- Even under auto-publish, validation gates remain mandatory:
  - required field completeness
  - sensitive content checks
  - image presence checks
  - provider health checks

### Publishing

- Publishing supports API and browser automation providers.
- Routing between providers is configuration-driven.
- Browser automation acts as the fallback path when API publish is unavailable or unhealthy.

### Provider Strategy

- LLM provider abstraction supports `OpenAI`, `Claude`, `Qwen`, and future vendors.
- Image generation starts with `gpt-image-1`.
- Provider outputs must be normalized into internal domain models before use.

## Technology Choices

- Backend: `FastAPI`, `Pydantic`, `SQLAlchemy`
- Database: `PostgreSQL`
- Queue: `Celery` with Redis as the broker and result backend
- Browser automation: `Playwright`
- LLM orchestration: `LangChain` used only inside provider and structured-generation layers
- Frontend: lightweight server-hosted web UI, favoring simple pages over a heavy SPA for phase one
- Storage: local filesystem first, behind a storage abstraction for later object storage migration

## Initial Repository Shape

```text
app/
  interfaces/
    rest/
    mcp/
    web/
  application/
  domain/
  infrastructure/
    collector/
    providers/
      llm/
      image/
      publisher/
      feishu/
  jobs/
  schemas/
tests/
  unit/
  integration/
  e2e/
docs/
  superpowers/
    specs/
    plans/
openspec/
  changes/
  specs/
```

## Risk Controls

- Crawl jobs enforce rate, batch, and concurrency limits.
- Every generation action stores provider, model, prompt, parameters, and timestamp snapshots.
- Publish attempts store provider, error code, response summary, and last successful checkpoint.
- Logs and job records carry correlation IDs for traceability.

## Testing Strategy

### Unit

- state machines
- provider routing rules
- validation and review gate policies

### Integration

- database persistence
- queue task dispatch and resume behavior
- provider adapters
- Feishu synchronization

### End-to-End

- minimal happy path from crawl to reviewed publish
- publish fallback from API provider to browser automation
- failure diagnostics for malformed model output and publish errors

### Observability Checks

- structured logs
- traceable job IDs
- retry records
- stage latency metrics

## Delivery Breakdown

The platform should be built as a sequence of focused changes rather than a single large implementation:

1. `bootstrap-xiaohongshu-content-platform`
   - repository skeleton, app bootstrap, config, persistence, queue, shared contracts
2. `add-xiaohongshu-collector`
   - Playwright crawler, parsing, filters, source post persistence
3. `add-analysis-and-topic-generation`
   - analysis reports and topic suggestion generation
4. `add-draft-and-image-generation`
   - draft generation, image assets, provider abstractions
5. `add-review-and-publish-flow`
   - review gate, publish jobs, provider switching, audit trail
6. `add-feishu-sync`
   - bitable synchronization and sync observability
7. `add-rest-mcp-and-web-ui`
   - operator interfaces over shared application services

## Recommended First Change

Start with `bootstrap-xiaohongshu-content-platform`. That change defines the modular monolith skeleton, domain contracts, provider abstractions, async job foundation, persistence model, and shared entrypoint patterns required by every later capability.
