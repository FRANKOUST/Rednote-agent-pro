# Operator Runbook

## 1. Startup

1. Install dependencies: `pip install -e .[dev]`
2. Copy env template: `copy .env.example .env`
3. Start the app: `uvicorn app.main:app --reload`
4. Open:
   - Web Console: `http://127.0.0.1:8000/`
   - OpenAPI: `http://127.0.0.1:8000/docs`

## 2. Recommended Safe Defaults

- `XHS_AUTH_ENABLED=true`
- `XHS_ALLOW_LIVE_PUBLISH=false`
- `XHS_DEFAULT_COLLECTOR_PROVIDER=playwright` only when storage state is available
- `XHS_ENABLE_REAL_*` flags off until validation day

## 3. Standard Operating Flow

1. Start a pipeline run
2. Inspect source posts and reports
3. Review generated drafts
4. Approve only the drafts worth sending forward
5. Publish in dry-run or safe-stub mode first
6. Inspect publish jobs, sync records, and diagnostics

## 4. Web Console Pages

- `/` dashboard
- `/console/entities` entity list
- `/console/source-posts/{id}`
- `/console/analysis-reports/{id}`
- `/console/topic-suggestions/{id}`
- `/console/image-assets/{id}`

## 5. Diagnostics

Use:

- `/api/pipeline-runs`
- `/api/pipeline-runs/{id}/diagnostics`
- `/api/providers/diagnostics`
- `/api/providers/health`
- `/api/audit-logs`

## 6. Worker Operation

### Inline

Use for quick local debugging.

### Background

Use for local async behavior.

### External worker

Use when you want a queue-manifest-backed execution path.

Recommended:

- `XHS_TASK_MODE=external_worker`
- `XHS_WORKER_ADAPTER_KIND=subprocess`

## 7. Recovery Steps

### Collector fallback

- Check provider diagnostics
- Check storage state path
- Re-run in safe mode if needed

### Model fallback

- Check API key and provider health
- Re-run using safe stubs if outputs are unstable

### Publish fallback

- Verify `XHS_ALLOW_LIVE_PUBLISH`
- Inspect publish job provider and mode
- Re-run using safe stub if needed

## 8. Operator Rules

- Do not enable live publish by default
- Do not bypass manual review
- Do not treat platform text as trusted input
- Do not run large uncontrolled keyword batches
