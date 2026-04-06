# OPERATOR RUNBOOK

## 1. Install / prepare

- Python 3.10+
- `pip install -e .[dev,collectors]`
- `scrapling install` if you want live browser fetchers
- install and authenticate `lark-cli`

## 2. Configure

Copy `.env.example` to `.env` and set at minimum:
- database/media paths
- `XHS_DEFAULT_COLLECTOR_PROVIDER=scrapling_xhs`
- `XHS_DEFAULT_SYNC_PROVIDER=feishu_cli`
- `XHS_DEFAULT_MODEL_PROVIDER=custom_model_router` or `openai_compatible`

## 3. Safe local verification

- Keep `XHS_SCRAPLING_MODE=fixture`
- Keep `XHS_FEISHU_CLI_DRY_RUN=true`
- Keep all `XHS_ENABLE_REAL_*` flags `false`
- Run `pytest -q`
- Start the app and trigger pipeline/collector/sync runs from REST or the Web Console

## 4. Controlled live collector validation

- Set `XHS_ENABLE_REAL_COLLECTOR=true`
- Set `XHS_SCRAPLING_MODE=live`
- Provide cookies/storage state
- Start with one keyword or one note id only
- Review `/api/providers/health`, `/api/collector-runs`, and `/api/pipeline-runs/{id}/diagnostics`

## 5. Controlled live model validation

- Set `XHS_ENABLE_REAL_MODEL_PROVIDER=true`
- Provide `XHS_MODEL_API_KEY`, `XHS_MODEL_BASE_URL`, `XHS_MODEL_NAME`
- Re-run a single dry pipeline request and confirm schema-validated outputs appear in reports/drafts

## 6. Controlled live sync validation

- Set `XHS_ENABLE_REAL_SYNC_PROVIDER=true`
- Set `XHS_FEISHU_CLI_DRY_RUN=false`
- Confirm `lark-cli --as <identity>` can reach the target Base
- Trigger `/api/sync-runs` before using the full pipeline

## 7. Publish safety

- Manual approval is always required before publish
- Leave `XHS_ALLOW_LIVE_PUBLISH=false` unless explicitly testing a safe live publisher
- Inspect `audit_logs`, `publish_jobs`, and `sync_records` after every publish attempt
