# Risks

## Active Risks

- Real Xiaohongshu scraping and publish automation require authenticated browser state and may break when DOM structure changes.
- Real provider credentials for OpenAI and Feishu are not available in the repository, so real integrations must remain optional.
- The repository is not a Git repository, so changes cannot be committed or reviewed through normal Git workflows yet.
- OpenSpec change names created during early planning do not fully match the final canonical breakdown requested by the product direction.
- Real provider implementations still lack credentials and platform permissions, so safe stubs remain the active path.
- The external worker adapter now writes queue manifests safely, but no standalone worker process consumes them yet.
- Entity-level REST and MCP reads now exist, but the Web Console still lacks dedicated pages for those entity views.
- Subprocess-backed external worker dispatch now exists, but it is still a local-process pattern rather than a durable distributed queue backend.

## Residual Risks At Completion

- Live provider shells still need validation against real credentials and platform behavior.
- The subprocess/file-backed worker adapters are suitable for safe local execution but not yet a durable production queue.
- Topic and image entities still expose richer detail through API/MCP than through the Web Console.

## Mitigations

- Build provider interfaces and safe mock implementations first.
- Keep crawl and publish behavior behind adapters with clear error classification.
- Record assumptions and backlog explicitly so real-integration work is visible and bounded.
- Introduce canonical OpenSpec change mapping and continue implementation against the canonical plan.

## Resolved in This Milestone

- The repository now has runnable code instead of planning-only assets.
- Core review, publish, sync, and audit records are now implemented and test-covered in mock mode.
- The three highest-priority canonical OpenSpec foundation changes now have complete artifacts and validated structure.
- The collector layer now has a safe Playwright adapter boundary, so real browser integration can be added without changing application services.
- Provider selection is now config-driven for mock and safe-real modes, reducing coupling before real credentials exist.
- API and MCP surfaces now have an operator-key baseline, but the Web Console still relies on deployment boundaries until session auth is added.
- Provider configuration is now visible to operators, but real provider health is still represented through safe-mode metadata rather than live remote checks.
- Web Console auth is now session-based, but there is still no fine-grained user or role model beyond the shared operator key.
- Live provider adapters now exist across collector/model/image/publish/sync, but none of the remote paths have been validated against real credentials or production guardrails yet.
- Generation-stage sync now exists, but real Feishu field mapping and idempotent external upsert semantics are not yet validated.
- The operator surfaces are now more visible, but provider health and stage diagnostics are still too shallow for real incident debugging.
