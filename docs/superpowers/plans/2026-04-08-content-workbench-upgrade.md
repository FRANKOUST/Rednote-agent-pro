# Content Workbench Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the existing Xiaohongshu content platform into a product-grade content workbench with explicit 8-stage orchestration, operator-facing schemas, staged publish/sync semantics, and unified REST/MCP/Web actions without rewriting the core architecture.

**Architecture:** Keep the current modular-monolith and provider registry, but split orchestration into a content pipeline service plus stage-level helpers. Persist richer stage events and business records, route every REST/MCP/Web action through the same service layer, and upgrade providers/schemas/prompts so crawl/analyze/topic/draft/image/review/publish/sync feel like real operator actions instead of generic framework steps.

**Tech Stack:** FastAPI, SQLAlchemy ORM, Pydantic v2, provider registry pattern, Jinja templates, pytest.

---

### Task 1: Audit gap + shared domain contract expansion

**Files:**
- Modify: `app/core/config.py`
- Modify: `app/domain/models.py`
- Modify: `app/domain/contracts.py`
- Modify: `app/db/models.py`
- Modify: `app/schemas.py`
- Test: `tests/unit/test_model_output_schemas.py`

- [ ] Add new configuration flags for staged pipeline execution, collector filtering defaults, publish safety defaults, and template registry defaults.
- [ ] Expand domain payloads and enums to cover the explicit 8-stage pipeline, operator review actions, publish prepare/preview/send, and sync_crawled/sync_generated semantics.
- [ ] Extend provider protocols so collectors can expose candidate/detail/filtering metadata and publishers can support prepare/preview/send through the shared service layer.
- [ ] Extend persistence models for richer stage summaries, upgraded analysis/topic/draft fields, publish preview artifacts, and sync business types.
- [ ] Add/adjust schema tests first for the new Pydantic contracts, then implement the domain/database changes to satisfy them.

### Task 2: Content pipeline orchestrator upgrade

**Files:**
- Modify: `app/application/services.py`
- Modify: `app/application/factory.py`
- Modify: `app/application/dispatcher.py`
- Modify: `app/application/external_worker.py`
- Test: `tests/integration/test_rest_pipeline_flow.py`
- Test: `tests/unit/test_dispatcher_modes.py`

- [ ] Write failing service/API tests for explicit stage execution, one-click runs, incremental stage runs, and stage diagnostics.
- [ ] Introduce a content pipeline service/orchestrator that models `crawl -> analyze -> topic -> draft -> image -> review -> publish -> sync` as explicit stages with state, provider, timestamps, input summary, output summary, and error capture.
- [ ] Keep dispatcher/external worker compatibility while ensuring every stage action routes through the same orchestrator entry points.
- [ ] Persist upgraded workflow summaries and stage events so diagnostics, audit logs, and workbench views can replay the run cleanly.

### Task 3: Two-phase collector semantics inside provider layer

**Files:**
- Modify: `app/infrastructure/providers/collector/mock.py`
- Modify: `app/infrastructure/providers/collector/safe_playwright.py`
- Modify: `app/infrastructure/providers/collector/scrapling_xhs.py`
- Modify: `app/infrastructure/providers/registry.py`
- Test: `tests/unit/test_scrapling_collector_provider.py`
- Test: `tests/unit/test_safe_playwright_collector.py`
- Test: `tests/integration/test_collector_and_sync_runs.py`

- [ ] Write failing collector tests for candidate collection, detail hydration, storage-state reuse metadata, filtering, and diagnostics.
- [ ] Refactor collector providers around `candidate collection -> detail hydration -> filtering -> final source posts` while keeping the provider registry intact.
- [ ] Add login-state reuse awareness (storage state preferred, cookies optional), content-type/ad/time/engagement/topic filters, and stage metadata that lands in diagnostics/audit paths.
- [ ] Preserve fixture/safe fallback behavior so the repo remains demoable without real credentials.

### Task 4: Operator-grade schemas + prompt template versioning

**Files:**
- Modify: `app/domain/model_schemas.py`
- Modify: `app/infrastructure/providers/llm/prompt_templates.py`
- Modify: `app/infrastructure/providers/llm/mock.py`
- Modify: `app/infrastructure/providers/llm/openai_compatible.py`
- Modify: `app/infrastructure/providers/llm/custom_model_router.py`
- Test: `tests/unit/test_model_output_schemas.py`
- Test: `tests/unit/test_model_provider_schema_validation.py`

- [ ] Write failing schema tests for enriched `AnalysisReport`, `TopicSuggestion`, and `ContentDraft` structures.
- [ ] Replace ad-hoc prompt builders with versioned prompt template definitions carrying template id, version, input fields, schema target, and purpose.
- [ ] Upgrade mock/live model providers to consume the template registry and validate structured outputs before returning domain payloads.
- [ ] Ensure image planning uses the same versioned prompt contract even when image generation stays on a separate provider.

### Task 5: Publish and sync business semantics

**Files:**
- Modify: `app/application/services.py`
- Modify: `app/infrastructure/providers/publisher/mock.py`
- Modify: `app/infrastructure/providers/publisher/api_safe_stub.py`
- Modify: `app/infrastructure/providers/publisher/browser_safe_stub.py`
- Modify: `app/infrastructure/providers/feishu/cli.py`
- Test: `tests/integration/test_publish_safety.py`
- Test: `tests/unit/test_feishu_cli_sync_provider.py`

- [ ] Write failing tests for `publish_prepare`, `publish_preview`, `publish_send`, `sync_crawled`, and `sync_generated`.
- [ ] Split publishing into prepare/preview/send while preserving the manual-review default and existing safety gate.
- [ ] Split sync into crawled/generated business types and persist that semantic type into sync runs/records.
- [ ] Update audit events, result summaries, and provider payload builders to use the new action names consistently.

### Task 6: REST, MCP, and Web workbench surface refactor

**Files:**
- Modify: `app/interfaces/rest/routes.py`
- Modify: `app/interfaces/mcp/routes.py`
- Modify: `app/interfaces/web/routes.py`
- Modify: `templates/index.html`
- Modify: `templates/providers.html`
- Modify: `templates/entities.html`
- Modify: `templates/diagnostics.html`
- Modify: `templates/entity_detail.html`
- Modify: `templates/run_list.html`
- Add: `templates/workbench.html` (or equivalent integrated dashboard sections)
- Test: `tests/integration/test_mcp_and_web.py`
- Test: `tests/integration/test_web_ops_pages.py`
- Test: `tests/integration/test_entity_rest_api.py`

- [ ] Write failing API/MCP/Web tests for one-click pipeline execution, stage-by-stage operations, run detail views, publish preview, sync actions, and provider/login checks.
- [ ] Normalize REST naming around runs, stages, publish actions, sync actions, and review actions.
- [ ] Replace the generic dashboard with a lightweight content assistant workbench showing 8 stages, artifacts, provider/error summaries, recent runs, provider health, and login/safety checks.
- [ ] Keep low-level queries and diagnostics available while adding the higher-level MCP operator tools requested by the spec.

### Task 7: Documentation + verification

**Files:**
- Modify: `README.md`
- Modify: `DEMO.md`
- Modify: `SHOWCASE.md`
- Modify: `REAL_OPS_READINESS.md`
- Modify: `OPERATOR_RUNBOOK.md`
- Modify: `PROVIDER_INTEGRATION_MATRIX.md`
- Modify: `ACCEPTANCE_CHECKLIST.md`
- Add: `CONTENT_PIPELINE_DESIGN.md`
- Add: `PROMPT_TEMPLATE_STRATEGY.md`
- Add: `PRODUCT_WORKBENCH_GUIDE.md`
- Modify: `assumptions.md`
- Modify: `progress.md`
- Modify: `risks.md`
- Modify: `backlog.md`

- [ ] Refresh the docs to describe the staged content workbench product, provider semantics, prompt strategy, operator runbook, and acceptance/demo flows.
- [ ] Update the process ledgers with assumptions, progress, residual risks, and remaining blocker-bound items only.
- [ ] Run focused pytest suites first, then the full test suite, and iterate until fresh verification evidence shows the repo is only blocked by real external credentials/logins (if at all).
