## 1. Collector domain and persistence model

- [ ] 1.1 Add source-post, crawl-run, and crawl-page diagnostic domain models and persistence schemas.
- [ ] 1.2 Add request and result schemas for keyword-based search collection with filter settings and crawl limits.
- [ ] 1.3 Add source fingerprint and deduplication policy utilities for collected Xiaohongshu posts.

## 2. Search navigation and extraction

- [ ] 2.1 Implement the Playwright collector adapter for Xiaohongshu search navigation and bounded pagination.
- [ ] 2.2 Implement result-card discovery and candidate extraction with layered selector fallbacks.
- [ ] 2.3 Add count parsing, content-type detection, and ad/video skip detection for candidate results.
- [ ] 2.4 Add optional detail-page enrichment for fields that are unavailable from the result-card view.

## 3. Eligibility filtering and persistence

- [ ] 3.1 Implement explicit eligibility checks for likes, favorites, comments, and supported content types.
- [ ] 3.2 Persist eligible results as normalized source-post snapshots with raw extraction evidence.
- [ ] 3.3 Apply deduplication behavior consistently across repeated crawl runs.

## 4. Crawl diagnostics and operator visibility

- [ ] 4.1 Persist crawl-run summaries, page-level counters, skip reasons, and extraction error categories.
- [ ] 4.2 Add partial-success workflow semantics and status retrieval for collector jobs.
- [ ] 4.3 Expose collector status and diagnostics through shared application services for later REST, MCP, and Web UI access.

## 5. Verification

- [ ] 5.1 Add unit tests for metric parsing, skip detection, source fingerprinting, and filter logic.
- [ ] 5.2 Add integration tests for async collector workflow dispatch and persistence of normalized source posts.
- [ ] 5.3 Add controlled Playwright integration coverage or fixture-based parser tests for representative Xiaohongshu result layouts.
- [ ] 5.4 Validate the `add-xiaohongshu-collector` OpenSpec change and document runtime prerequisites for browser state and login handling.
