## ADDED Requirements

### Requirement: Pipeline execution SHALL be routed through a dispatcher abstraction
The system SHALL execute pipeline work through a dispatcher abstraction that supports at least local inline execution and a background execution mode.

#### Scenario: Inline dispatch
- **WHEN** task mode is configured as `inline`
- **THEN** the dispatcher executes the task immediately in the application process

#### Scenario: Background dispatch
- **WHEN** task mode is configured as `background`
- **THEN** the dispatcher returns a background handle while still executing the task through the dispatcher boundary

### Requirement: Orchestration SHALL remain interface-agnostic
The system SHALL expose the same workflow-run contract regardless of whether the run was started from REST, MCP, or Web.

#### Scenario: Shared run contract
- **WHEN** different operator interfaces start the same pipeline action
- **THEN** they receive workflow-run data in the same structural form
