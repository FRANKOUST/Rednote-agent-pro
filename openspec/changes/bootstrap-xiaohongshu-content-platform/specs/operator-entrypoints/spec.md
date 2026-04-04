## ADDED Requirements

### Requirement: REST, MCP, and Web UI SHALL share use-case services
The system SHALL expose operator actions through REST routes, MCP tools, and Web UI handlers that delegate to the same application-layer use cases.

#### Scenario: Shared operator behavior
- **WHEN** a capability is triggered through REST and through MCP
- **THEN** both entrypoints execute the same underlying use case and apply the same business rules

### Requirement: Entry points SHALL expose trackable workflow handles
The system SHALL return stable identifiers or references that let operators inspect asynchronous workflow progress across interface types.

#### Scenario: Track job from any interface
- **WHEN** an async workflow is started from the Web UI
- **THEN** the returned workflow reference can also be queried through a programmatic interface such as REST or MCP

### Requirement: Interface validation SHALL be consistent
The system SHALL validate operator input through shared schemas so that equivalent requests behave consistently across REST, MCP, and Web UI submissions.

#### Scenario: Consistent invalid request handling
- **WHEN** an operator submits an invalid request payload through any supported interface
- **THEN** the system rejects the request using the same validation rules and returns a structured error response suitable for that interface
