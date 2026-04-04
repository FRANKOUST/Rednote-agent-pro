## ADDED Requirements

### Requirement: Eligible results SHALL be persisted as normalized source-post snapshots
The system SHALL persist each eligible Xiaohongshu result as a normalized source-post snapshot containing canonical post identifiers or URLs, textual fields, parsed metrics, and crawl provenance.

#### Scenario: Persist normalized source post
- **WHEN** the collector determines that a candidate result is eligible
- **THEN** it writes a normalized source-post snapshot with crawl metadata and extracted metrics

### Requirement: Source-post records SHALL support deduplication
The system SHALL compute a stable source fingerprint so repeated collector runs do not create uncontrolled duplicates for the same source content within the same deduplication policy.

#### Scenario: Deduplicate repeated result
- **WHEN** a later collector run encounters a result with the same source fingerprint under the same deduplication policy
- **THEN** the system reuses or links the existing source identity instead of creating an uncontrolled duplicate entry

### Requirement: Source-post persistence SHALL preserve raw extraction evidence
The system SHALL retain enough raw extraction context, such as original metric strings, source URLs, or extraction metadata, to support later audit and parsing verification.

#### Scenario: Retain extraction evidence
- **WHEN** a source-post snapshot is persisted
- **THEN** the stored record includes raw extraction evidence needed to explain how normalized fields were derived
