## Context

The platform foundation defines async workflows, provider boundaries, and shared entrypoints, but it does not yet collect any Xiaohongshu data. This change introduces the first high-variance external integration: browser-driven search crawling. The collector must turn Xiaohongshu search results into normalized `SourcePost` records that later analysis and topic-generation changes can consume.

The collector operates under several constraints:
- Search crawling must be queue-backed and stage-aware, not tied to request lifecycles.
- The system only needs internal-team scale in phase one, but it must still enforce bounded concurrency and pacing.
- Collector outputs must be durable snapshots because downstream analysis depends on reproducible source evidence.
- The crawler must skip ads and video posts, and support threshold filters on likes, favorites, and comments.
- Failures must be diagnosable enough for operators to see whether the run failed because of login state, page layout change, rate limiting, or extraction mismatch.

## Goals / Non-Goals

**Goals:**
- Add Playwright-based Xiaohongshu search collection with keyword-driven crawl jobs.
- Normalize extracted results into persisted source-post snapshots and crawl-run metadata.
- Support filter rules for engagement thresholds and content-type exclusion.
- Add structured diagnostics, partial-success reporting, and retry-safe crawl behavior.
- Preserve enough page metadata to let later changes trace topics and drafts back to original source posts.

**Non-Goals:**
- Building a generalized web crawler framework for arbitrary websites.
- Solving anti-detection or stealth hardening beyond bounded pacing and stable browser-state reuse.
- Supporting comments, author-profile crawling, or deep post-detail enrichment in this change.
- Publishing content or generating analysis, topics, or drafts.

## Decisions

### Decision: Use search-result crawling first, with detail-page visits only when required

The collector SHALL primarily parse Xiaohongshu search result cards and only open detail pages when critical fields are missing from the list result. This reduces crawl cost and lowers the chance of triggering aggressive platform defenses.

Alternatives considered:
- Always open detail pages: rejected because it multiplies browser actions and failure surface.
- Only parse list pages with no fallback: rejected because some cards may omit normalized fields needed downstream.

### Decision: Model crawl as a two-stage pipeline

Each collector job SHALL run in two logical stages: `discover_result_cards` and `extract_normalized_posts`. Discovery collects candidate cards and lightweight metadata. Extraction applies skip/filter rules, resolves missing fields, and writes normalized snapshots.

Alternatives considered:
- Single monolithic parse pass: rejected because it makes partial failures hard to classify.
- Multi-page graph crawl: rejected because phase one only needs search-result bounded collection.

### Decision: Use normalized source-post snapshots with source fingerprints

Each collected post SHALL be stored as an immutable snapshot with a stable deduplication fingerprint based on source platform, post identifier or canonical URL, and crawl context. Metrics captured during a crawl stay attached to that snapshot and are not retroactively overwritten.

Alternatives considered:
- Mutable "latest state" post records: rejected because analysis later needs reproducible historical evidence.
- Raw HTML-only storage: rejected because downstream services need normalized fields, not only opaque blobs.

### Decision: Separate eligibility filtering from extraction

The collector SHALL first extract a candidate shape, then run explicit eligibility checks for ad/video detection and engagement thresholds before persisting the record as a valid `SourcePost`. Rejected candidates still contribute to crawl diagnostics.

Alternatives considered:
- Filter while scraping individual DOM fields: rejected because it makes diagnostics too implicit.
- Persist everything and filter later: rejected because downstream services would need to repeat eligibility logic and deal with noisy data.

### Decision: Treat crawl diagnostics as first-class records

Each crawl job SHALL persist summary diagnostics, per-page counters, skip reasons, and structured extraction errors. Operators need visibility into partial success rather than a binary pass/fail result.

Alternatives considered:
- Logging only to stdout or application logs: rejected because operators and MCP clients need structured status retrieval.

## Risks / Trade-offs

- [Xiaohongshu DOM changes break selectors] → Use layered selectors, extraction fallbacks, and explicit extraction-error categories instead of brittle single-path parsing.
- [Browser login state expires or becomes invalid] → Detect and classify authentication-state failures early in the crawl and stop with actionable diagnostics.
- [Crawl pace triggers throttling or unstable results] → Enforce per-job page caps, inter-action delay ranges, and limited concurrency.
- [Threshold filters may discard useful content if counts are parsed incorrectly] → Normalize count parsing centrally and record raw metric strings alongside parsed integers when possible.
- [Deduplication may collapse distinct snapshots] → Use source fingerprint plus crawl context and keep immutable snapshot records instead of overwriting prior data.

## Migration Plan

1. Add source-post and crawl-run persistence models on top of the platform foundation.
2. Implement search query request schemas and collector application services.
3. Add the Playwright collector adapter for search navigation, result discovery, and extraction.
4. Add eligibility filtering, deduplication, and persistence wiring.
5. Add crawl diagnostics and operator-facing status retrieval.
6. Verify crawl behavior with mocked extraction tests and controlled integration runs before enabling broader execution.

Rollback strategy:
- Revert collector-specific routes, services, models, and jobs while leaving the foundation intact.
- If partial crawl data exists, isolate it by table or workflow type so the change can be disabled without breaking the rest of the platform.

## Open Questions

- Which exact Xiaohongshu search URL pattern and query parameters should be treated as canonical for phase-one collection?
- Should page screenshots or raw HTML fragments be stored for failed extraction debugging, or is structured error context sufficient?
- What is the default maximum page count per crawl job for phase one?
