## ADDED Requirements

### Requirement: REST SHALL expose core workflow operations
The system SHALL expose REST endpoints to create workflow runs, inspect runs, review drafts, publish drafts, and inspect publish, sync, audit, and provider-diagnostic records.

#### Scenario: Start a pipeline run over REST
- **WHEN** an operator submits a valid pipeline request to the REST API
- **THEN** the system creates or dispatches a workflow run and returns a trackable run payload

#### Scenario: Inspect diagnostics over REST
- **WHEN** an operator requests diagnostics for a workflow run
- **THEN** the API returns stage-level diagnostics including provider context

### Requirement: Protected REST endpoints SHALL enforce operator auth when enabled
The system SHALL require the configured operator key header on protected REST endpoints whenever auth mode is enabled.

#### Scenario: Reject unauthorized request
- **WHEN** auth is enabled and a protected REST endpoint is called without the correct operator key
- **THEN** the API responds with an unauthorized error
