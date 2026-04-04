## ADDED Requirements

### Requirement: Collector SHALL run keyword-based Xiaohongshu search jobs
The system SHALL accept one or more search keywords and create an asynchronous collector workflow that navigates Xiaohongshu search results for each keyword.

#### Scenario: Start search collection workflow
- **WHEN** an operator submits a collector request with at least one keyword
- **THEN** the system creates a trackable async workflow for Xiaohongshu search collection

### Requirement: Collector SHALL support engagement and content filters
The system SHALL support request-level filters for minimum likes, minimum favorites, minimum comments, and exclusion of unsupported content types such as video.

#### Scenario: Filter eligible card results
- **WHEN** the collector extracts a candidate result card
- **THEN** it evaluates the parsed metrics and content type against the request filters before marking the card as eligible

### Requirement: Collector SHALL skip ads and video posts
The collector SHALL detect and reject search results that are identified as advertisements or videos, even if they otherwise satisfy the engagement thresholds.

#### Scenario: Skip ad result
- **WHEN** a search result contains an ad signal
- **THEN** the collector excludes it from persisted source-post results and records the skip reason in diagnostics

#### Scenario: Skip video result
- **WHEN** a search result is identified as video content
- **THEN** the collector excludes it from persisted source-post results and records the skip reason in diagnostics

### Requirement: Collector SHALL use bounded search traversal
The collector SHALL enforce bounded traversal controls such as maximum page count or result count so a collection run stays finite and operationally predictable.

#### Scenario: Stop after crawl limit
- **WHEN** the collector reaches the configured page or result limit for a request
- **THEN** it stops traversal and completes the workflow with the results collected so far
