## ADDED Requirements

### Requirement: The platform SHALL model the core content workflow entities
The system SHALL maintain explicit entities for `SourcePost`, `AnalysisReport`, `TopicSuggestion`, `ContentDraft`, `ImageAsset`, `PublishJob`, and `SyncRecord`.

#### Scenario: Persist pipeline outputs by entity type
- **WHEN** a pipeline run progresses through crawl, analysis, generation, publish, and sync stages
- **THEN** each stage persists its outputs into the corresponding domain entity type instead of mixing all data into a single generic record

### Requirement: Audit records SHALL be modeled separately from business entities
The system SHALL store operational audit events independently from content and publish records.

#### Scenario: Record operator approval
- **WHEN** an operator approves a draft
- **THEN** the system stores an audit record for that action without mutating unrelated business entities beyond the draft lifecycle change
