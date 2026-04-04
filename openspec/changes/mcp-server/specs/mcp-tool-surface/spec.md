## ADDED Requirements

### Requirement: MCP SHALL list available tools
The system SHALL expose a tool-listing method that returns the currently supported operator tools.

#### Scenario: List tools
- **WHEN** an MCP client requests the tool list
- **THEN** the system returns the available tool names and input schemas

### Requirement: MCP SHALL call shared workflow tools
The system SHALL expose tool calls for starting pipeline runs and listing key records through the same shared service layer used by other interfaces.

#### Scenario: Start pipeline from MCP
- **WHEN** an MCP client calls the pipeline-start tool
- **THEN** the system returns the same workflow-run structure used by other operator interfaces
