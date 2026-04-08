# Progress

## 2026-04-06

- Audited the existing MediaCrawler, legacy Feishu sync, and single-vendor model coupling points.
- Replaced the collector integration path with `scrapling_xhs` registered through the shared provider registry.
- Added Scrapling search/detail fixture harnesses, extractor logic, diagnostics metadata, retry classification, and run persistence wiring.
- Reworked Feishu sync to run through `feishu_cli`/`lark-cli` command building, dry-run payload building, structured result parsing, and SyncRecord persistence.
- Reworked language-model integration to support `openai_compatible` and `custom_model_router` providers driven by unified env settings.
- Updated image-provider config to follow the same OpenAI-compatible env structure when enabled.
- Wired provider diagnostics and health through REST, MCP, and the Web Console provider-status page.
- Added new root docs: `DEMO.md`, `SHOWCASE.md`, `SCRAPLING_INTEGRATION.md`, `MODEL_PROVIDER_INTEGRATION.md`.
- Replaced MediaCrawler-oriented docs/config with Scrapling/lark-cli/model-router operator docs.
- Replaced outdated provider tests and verified the repository with `pytest -q` (`54 passed`).

## 2026-04-08

- Audited the repo against the new content workbench brief and wrote the execution plan to `docs/superpowers/plans/2026-04-08-content-workbench-upgrade.md`.
- Upgraded the shared business layer into an explicit 8-stage content pipeline service with full-run and staged execution modes.
- Reworked crawl semantics around candidate collection, detail hydration, filtering, login-state reuse metadata, and SourcePost/run/audit/diagnostics integration.
- Rebuilt the analysis/topic/draft/image-planning contracts into operator-facing schemas backed by versioned prompt templates.
- Split publishing into prepare/preview/send and sync into sync_crawled/sync_generated semantics while keeping the safety gate and dry-run defaults.
- Reworked REST, MCP, and Web surfaces into a content assistant workbench while preserving legacy aliases for compatibility.
- Refreshed README, demo/showcase, runbook, readiness, design, prompt, and workbench docs around the new productized flow.
- Re-verified the repository with `pytest -q` (`56 passed`).

## Current State

The repo now meets the requested “产品层升级 + schema 重构 + 发布与同步语义重构 + MCP/Web 前台重构” bar in code/tests/docs. Remaining work is limited to real external credential/login validation.
