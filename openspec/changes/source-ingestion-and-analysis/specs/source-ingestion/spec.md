## ADDED Requirements

### Requirement: The platform SHALL persist collected source posts
The system SHALL persist collected source posts with keyword, metrics, URL, tags, and run linkage.

#### Scenario: Collect source posts
- **WHEN** a pipeline run completes its collection stage
- **THEN** the resulting source posts are queryable through persisted records

### Requirement: The collector SHALL support safe fallback behavior
The system SHALL fall back safely when a configured real collector cannot run because of missing dependencies, missing browser state, or runtime errors.

#### Scenario: Safe collector fallback
- **WHEN** the real collector path cannot execute successfully
- **THEN** the system returns fallback-collected source posts rather than failing the entire run by default
