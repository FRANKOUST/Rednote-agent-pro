## ADDED Requirements

### Requirement: The platform SHALL persist publish jobs
The system SHALL persist publish jobs including status, provider, mode, and published URL.

#### Scenario: Record publish job
- **WHEN** a draft is published
- **THEN** the system stores a publish job record with the actual executing provider and result
