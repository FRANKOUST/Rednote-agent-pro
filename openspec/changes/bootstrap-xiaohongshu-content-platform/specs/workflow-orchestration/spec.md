## ADDED Requirements

### Requirement: Long-running workflows SHALL execute asynchronously
The system SHALL run multi-stage content workflows through a queue-backed async execution model instead of blocking HTTP or MCP request threads.

#### Scenario: Async workflow dispatch
- **WHEN** an operator starts a pipeline-oriented action
- **THEN** the system returns a trackable job reference and executes the workflow asynchronously

### Requirement: Workflows SHALL persist stage checkpoints
The system SHALL record workflow stage status and enough checkpoint data to support resume, retry, and diagnostics from the failed stage.

#### Scenario: Retry from failed stage
- **WHEN** a workflow fails during a later stage
- **THEN** the operator can inspect the failed stage and rerun from that stage without rerunning all completed upstream stages

### Requirement: Workflow failures SHALL be structured
The system SHALL classify workflow failures with stable error metadata, including retryability and provider context when relevant.

#### Scenario: Structured job failure
- **WHEN** an async workflow fails
- **THEN** the recorded job result contains an error code, human-readable message, retryability flag, and relevant stage or provider context
