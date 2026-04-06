# REAL_OPS_READINESS

## Ready Now

- Scrapling provider wiring, selector/extractor harness, dry-run fixtures, diagnostics, and run persistence.
- lark-cli sync provider wiring, Base payload builder, dry-run command path, result parsing, retry metadata, and SyncRecord persistence.
- Unified model-provider env configuration, OpenAI-compatible invocation path, router abstraction, schema validation, and safe fallback.
- REST / MCP / Web provider status visibility plus run-level diagnostics.
- Test-covered end-to-end dry-run workflow (`54 passed`).

## Remaining Real Blockers

1. Real XHS collection material
   - `XHS_SCRAPLING_MODE=live`
   - valid cookies and/or storage state for the target account
2. Real Feishu CLI environment
   - installed/authenticated `lark-cli`
   - target Base token + table id (or Sheet token/range)
3. Real model vendor credentials
   - `XHS_MODEL_API_KEY`
   - `XHS_MODEL_BASE_URL`
   - `XHS_MODEL_NAME`

## Ready-for-validation Sequence

1. Run Scrapling search/detail in controlled low-volume mode.
2. Run the full pipeline with review-only publish.
3. Execute Feishu sync dry-run, then live sync.
4. Capture results in `SMALL_SCALE_VALIDATION_REPORT.md`.
