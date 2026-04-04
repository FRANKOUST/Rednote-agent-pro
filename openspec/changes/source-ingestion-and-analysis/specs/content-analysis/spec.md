## ADDED Requirements

### Requirement: The platform SHALL persist analysis reports
The system SHALL persist an analysis report for each completed generation run that includes a summary, top keywords, and top tags.

#### Scenario: Persist report
- **WHEN** the analysis stage completes
- **THEN** the system stores a report linked to the originating run

### Requirement: The platform SHALL persist topic suggestions
The system SHALL persist topic suggestions linked to an analysis report.

#### Scenario: Persist topics
- **WHEN** the topic-generation stage completes
- **THEN** the system stores topic suggestions linked to the report and run
