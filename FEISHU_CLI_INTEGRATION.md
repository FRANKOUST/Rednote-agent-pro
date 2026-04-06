# FEISHU CLI Integration

## Provider

- Registry key: `feishu_cli`
- Runtime adapter: `app/infrastructure/providers/feishu/cli.py`
- Primary sync mode: `base`

## Flow

1. Service builds a sync payload.
2. `feishu_cli` provider maps fields using `config/feishu_field_mapping.json`.
3. Provider builds a `lark-cli` command.
4. Dry-run returns a structured result immediately; live mode captures stdout/stderr, timeout, and retry metadata.
5. `SyncRun` and `SyncRecord` persist the result.

## Key envs

- `XHS_FEISHU_CLI_BIN`
- `XHS_FEISHU_CLI_AS`
- `XHS_FEISHU_SYNC_MODE`
- `XHS_FEISHU_BASE_TOKEN`
- `XHS_FEISHU_TABLE_ID`
- `XHS_FEISHU_CLI_DRY_RUN`
- `XHS_FEISHU_FIELD_MAPPING_PATH`

## Readiness

Dry-run is ready now. Real validation still needs an authenticated `lark-cli` environment and a target Base.
