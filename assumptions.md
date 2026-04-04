# Assumptions

- The repository has no production code yet, so the fastest path is to build a fresh modular-monolith baseline rather than preserve nonexistent implementation.
- Local demo mode uses SQLite by default for zero-friction startup, while the architecture and schema remain PostgreSQL-compatible.
- Background workflow execution is abstracted behind an internal dispatcher; the default local implementation runs jobs in-process so the demo works without Redis or Celery.
- External providers are stubbed or mocked by default unless credentials are present. Real OpenAI, Feishu, and Xiaohongshu integrations remain pluggable.
- The first runnable milestone prioritizes a full mocked happy-path pipeline: `crawl -> analyze -> topic -> draft -> image -> review -> publish -> sync`.
- MCP support is delivered as a minimal HTTP JSON-RPC tool server over shared application services in phase one.
- The web console is a lightweight server-rendered operator UI aimed at demos and internal operation, not a polished SPA.
- Authentication is kept minimal for the single-team phase and enforced through local configuration boundaries rather than full multi-user RBAC.
