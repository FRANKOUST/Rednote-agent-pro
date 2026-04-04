## Why

The platform cannot analyze competitor behavior or generate grounded content ideas until it can reliably collect Xiaohongshu search results and persist them as structured source data. Crawling must be implemented as a bounded, diagnosable capability because it is the highest-variance integration in the system.

## What Changes

- Add Playwright-driven Xiaohongshu search collection jobs.
- Support keyword-based crawling with filters for likes, favorites, comments, and content type.
- Skip ads and video posts based on page signals and extraction rules.
- Persist normalized source post snapshots and crawl diagnostics.
- Add deduplication, rate limiting, and retry-safe crawl job behavior.

## Capabilities

### New Capabilities

- `xiaohongshu-search-collection`: Search crawling, pagination, filtering, and result extraction from Xiaohongshu.
- `source-post-persistence`: Normalized storage of collected post snapshots, metrics, and crawl metadata.
- `crawl-diagnostics`: Structured crawl logs, extraction errors, and operator-visible job diagnostics.

### Modified Capabilities

None.

## Impact

- Affects Playwright runtime support, async workflow stages, source-content persistence, and future analysis inputs.
- Introduces selector management, anti-fragile parsing, and crawl pacing concerns.
- Requires local browser state handling and observable failure metadata.
