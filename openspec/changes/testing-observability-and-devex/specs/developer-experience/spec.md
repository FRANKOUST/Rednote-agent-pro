## ADDED Requirements

### Requirement: The project SHALL support documented local startup
The system SHALL provide environment templates and startup instructions that let a developer run the platform locally.

#### Scenario: Local startup path
- **WHEN** a developer follows the documented startup steps
- **THEN** the platform boots successfully in local mode

### Requirement: The project SHALL maintain automated regression coverage
The system SHALL provide automated tests for core state-machine, dispatcher, auth, provider, and end-to-end workflow behavior.

#### Scenario: Run regression suite
- **WHEN** the test suite is executed
- **THEN** it verifies the main mocked workflow and operator surfaces
