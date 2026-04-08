# Risks

## Active Risks

- Real Xiaohongshu collection still needs a valid authenticated Scrapling or Playwright session (storage state preferred, cookies optional) and may require selector maintenance when XHS markup changes.
- Real Feishu sync still needs an authenticated `lark-cli` environment with the target Base or Sheet granted to that identity.
- Real model validation still needs at least one provider API key, base URL, and model that accept OpenAI-compatible chat completion requests.
- Real publish validation still needs browser/API credentials and should only happen after manual operator approval.
- The queue/worker layer remains suitable for controlled small-scale operation, not durable large-scale distributed execution.

## Mitigations

- Keep every external integration behind provider/adapter/registry boundaries.
- Default collector and sync verification to dry-run/fixture mode until credentials are supplied.
- Enforce schema validation on model output and safe fallback when live execution is disabled or invalid.
- Preserve audit logs, run diagnostics, sync records, and publish safety gates on every mutating path.
- Keep Web / REST / MCP behavior aligned through the same service layer so fixes land once.

## Residual Completion Risks

- Real-world DOM drift, CLI output changes, and vendor-specific OpenAI-compatible quirks may require small follow-up adapter tweaks after credentials are provided.
