## ADDED Requirements

### Requirement: Crawl runs SHALL expose structured diagnostics
The system SHALL persist crawl-run diagnostics including workflow status, pages visited, candidate counts, persisted result counts, and categorized skip reasons.

#### Scenario: View crawl summary
- **WHEN** an operator inspects a completed or failed crawl run
- **THEN** the system returns a structured diagnostic summary instead of only a binary success flag

### Requirement: Extraction failures SHALL be classified
The system SHALL classify extraction failures using stable categories such as authentication failure, page-load failure, selector mismatch, and metric-parse failure.

#### Scenario: Classify extraction mismatch
- **WHEN** the collector cannot extract a required field because expected page selectors no longer match
- **THEN** the crawl diagnostics record a selector-mismatch classification for that failure

### Requirement: Collector SHALL support partial success completion
The system SHALL allow a crawl run to complete with partial success when at least some eligible results were collected, while still surfacing the skipped and failed portions in diagnostics.

#### Scenario: Partial success crawl
- **WHEN** one page of a multi-page crawl fails after earlier pages have already yielded eligible results
- **THEN** the workflow may finish in a partial-success state with collected results and a diagnostic record of the failed page
