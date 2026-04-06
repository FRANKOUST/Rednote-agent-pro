# SECURITY_GUARDRAILS

- Default all external integrations to fixture, mock, safe stub, or dry-run mode.
- Do not implement anti-captcha, anti-risk-control, or platform-evasion logic in the collector.
- Keep publish manual-review-first and live-publish disabled unless explicitly enabled.
- Validate every model response through schema guards before it touches business logic.
- Persist audit logs, sync records, collector runs, and pipeline stage diagnostics for every meaningful operator action.
- Limit real-world validation to small, controlled, low-concurrency runs.
- Treat cookies, storage state, API keys, and CLI auth as operator-managed secrets; never hardcode them.
