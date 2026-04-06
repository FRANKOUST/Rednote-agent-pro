# Acceptance Checklist

## Architecture

- [x] REST, MCP, and Web Console share one business layer
- [x] Provider registry owns collector / model / sync selection
- [x] Safety gates remain in front of publish and live external actions

## Collector

- [x] `scrapling_xhs` provider is wired through the registry
- [x] Search collection path works in fixture/dry-run mode
- [x] Detail collection path works in fixture/dry-run mode
- [x] Collector runs persist diagnostics and summaries
- [ ] Real authenticated Scrapling validation recorded

## Sync

- [x] `feishu_cli` provider is wired through the registry
- [x] Base-first payload + command builder exists
- [x] Dry-run sync path records SyncRun and SyncRecord
- [x] CLI stdout/stderr and retry metadata are captured into diagnostics
- [ ] Real authenticated lark-cli validation recorded

## Model

- [x] Unified env-driven model provider config exists
- [x] `openai_compatible` provider exists
- [x] `custom_model_router` provider exists
- [x] Analyze / topic / draft stages use the shared provider path
- [x] Schema validation guards model output
- [ ] Real model-provider validation recorded

## Operator Experience

- [x] Dashboard shows provider health and recent runs
- [x] Web Console exposes collector runs, sync runs, and provider status
- [x] REST exposes diagnostics / health / run details
- [x] MCP exposes collector search/detail and provider status tools

## Validation

- [x] Test suite passes (`54 passed`)
- [ ] Full small-scale real validation report completed with external credentials
