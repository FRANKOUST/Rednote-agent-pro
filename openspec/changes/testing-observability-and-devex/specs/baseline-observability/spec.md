## ADDED Requirements

### Requirement: The platform SHALL attach request identifiers to responses
The system SHALL include a request identifier header on HTTP responses for traceability.

#### Scenario: Read request id
- **WHEN** an operator calls an HTTP endpoint
- **THEN** the response includes the configured request-id header

### Requirement: The platform SHALL expose queryable diagnostics
The system SHALL expose observability summaries and run/provider diagnostics through operator-facing endpoints.

#### Scenario: Query observability summary
- **WHEN** an operator requests the observability summary
- **THEN** the system returns counts for workflow, publish, sync, and audit records
