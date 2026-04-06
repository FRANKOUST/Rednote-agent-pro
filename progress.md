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

## Current State

The project now reaches the requested “small-scale real-use ready except external credentials/login state” stage:
- Collector: Scrapling provider wired, search/detail dry-run harness ready.
- Sync: lark-cli provider wired, Base-first command path ready.
- Model: env-driven OpenAI-compatible/router path ready for analyze/topic/draft.
- Surfaces: REST / MCP / Web share the same service layer and provider status visibility.
