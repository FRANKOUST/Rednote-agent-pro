# Xiaohongshu Content Platform Roadmap

## Purpose

This roadmap turns the approved platform design into a staged OpenSpec delivery program. Each change is intentionally narrower than the overall product so the team can validate architecture, interfaces, and operational behavior incrementally.

## Delivery Sequence

### 1. `bootstrap-xiaohongshu-content-platform`

Create the platform skeleton, queue foundation, persistence base, provider contracts, and shared interface patterns.

Depends on: none

### 2. `add-xiaohongshu-collector`

Implement Playwright-based search collection, filtering, deduplication, snapshot persistence, and crawl-job diagnostics.

Depends on:
- `bootstrap-xiaohongshu-content-platform`

### 3. `add-analysis-and-topic-generation`

Turn collected source posts into structured analysis reports and AI-generated topic suggestions with traceable rationale.

Depends on:
- `bootstrap-xiaohongshu-content-platform`
- `add-xiaohongshu-collector`

### 4. `add-draft-and-image-generation`

Generate content drafts, titles, tags, CTA suggestions, image prompts, and local image assets through pluggable model providers.

Depends on:
- `bootstrap-xiaohongshu-content-platform`
- `add-analysis-and-topic-generation`

### 5. `add-review-and-publish-flow`

Implement manual review as the default gate, configurable auto-publish, publish provider routing, browser automation fallback, and publish audit records.

Depends on:
- `bootstrap-xiaohongshu-content-platform`
- `add-draft-and-image-generation`

### 6. `add-feishu-sync`

Sync scraped records, analysis outputs, generated drafts, and publish outcomes into Feishu Bitable for team collaboration and review tracking.

Depends on:
- `bootstrap-xiaohongshu-content-platform`
- `add-xiaohongshu-collector`
- `add-draft-and-image-generation`
- `add-review-and-publish-flow`

### 7. `add-rest-mcp-and-web-ui`

Expose the platform through production-ready REST APIs, MCP tools, and a usable operator web interface over the shared application layer.

Depends on:
- `bootstrap-xiaohongshu-content-platform`
- `add-xiaohongshu-collector`
- `add-analysis-and-topic-generation`
- `add-draft-and-image-generation`
- `add-review-and-publish-flow`

## Recommended Milestones

### Milestone A: Platform foundation

- `bootstrap-xiaohongshu-content-platform`

### Milestone B: Insight generation

- `add-xiaohongshu-collector`
- `add-analysis-and-topic-generation`

### Milestone C: Content factory

- `add-draft-and-image-generation`

### Milestone D: Human-in-the-loop publishing

- `add-review-and-publish-flow`
- `add-feishu-sync`

### Milestone E: Operator surfaces

- `add-rest-mcp-and-web-ui`

## Execution Notes

- Keep OpenSpec changes separate even if some code lands in the same modules.
- Archive each change only after acceptance tests for that change pass.
- Do not let REST, MCP, and Web UI reintroduce business logic that belongs in shared services.
- Treat browser automation publish as a provider implementation, not as a parallel business workflow.
