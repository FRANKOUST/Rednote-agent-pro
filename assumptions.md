# Assumptions

- The existing FastAPI modular-monolith remains the shared business hub; all upgrades extend the current REST, MCP, Web Console, dispatcher, worker, registry, and persistence layers rather than replacing them.
- Two-phase crawl semantics stay inside collector providers; routes and templates never own candidate/detail/filtering logic.
- Publishing remains manual-review-first and dry-run-first by default; the publish safety gate stays enabled unless operators intentionally relax it later.
- Feishu sync continues to flow through `lark-cli` / `feishu_cli`; no new runtime SDK dependency was introduced.
- Model generation remains provider-agnostic and schema-bound through versioned prompt templates plus safe fallback behavior.
- The repo still uses local/test `create_all` bootstrap semantics instead of a formal migration tool, so persistence evolution stays additive and compatible with clean bootstraps.
- Real external validation (XHS login, live publish, Feishu auth, model API keys) remains outside the repo and can only be completed once the operator supplies credentials/permissions.
