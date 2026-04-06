# Assumptions

- The current FastAPI modular-monolith remains the only business hub; all new integrations extend the existing REST, MCP, Web Console, dispatcher, worker, registry, and persistence layers.
- Scrapling runs inside a collector provider boundary and defaults to fixture/dry-run mode until a real authenticated small-scale environment is supplied.
- Feishu sync runs through `lark-cli` only; runtime Feishu SDK coupling is intentionally avoided.
- Model access is provider-configured through OpenAI-compatible endpoints plus a router abstraction, with schema validation and safe fallback required on every stage.
- Publishing remains manual-review-first and dry-run-first; no automatic live publish path is enabled by default.
- The repository target is learning-use, small-scale, controlled operation with full diagnostics and auditability rather than high-volume automation.
