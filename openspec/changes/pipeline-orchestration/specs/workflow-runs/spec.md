## ADDED Requirements

### Requirement: Pipeline execution SHALL create persisted workflow-run records
The system SHALL persist a workflow-run record whenever an operator starts the content pipeline.

#### Scenario: Create trackable run
- **WHEN** an operator starts the pipeline through REST, MCP, or Web
- **THEN** the system creates a workflow-run record with a stable identifier and status metadata

### Requirement: Workflow runs SHALL expose stage and status metadata
The system SHALL record both overall workflow status and current stage so callers can inspect progress.

#### Scenario: Read workflow progress
- **WHEN** an operator queries a workflow run
- **THEN** the response includes the run status and its current or most recent stage
