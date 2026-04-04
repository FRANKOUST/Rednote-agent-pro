## ADDED Requirements

### Requirement: The Web Console SHALL expose core operator actions
The system SHALL provide a Web Console where an operator can start a pipeline, review drafts, publish approved drafts, and inspect recent run, publish, sync, and audit information.

#### Scenario: Approve from console
- **WHEN** an operator uses the Web Console to approve a draft
- **THEN** the draft transitions through the same review flow used by the other interfaces

### Requirement: Auth-enabled console access SHALL require login
The system SHALL redirect unauthenticated Web Console requests to a login page whenever auth mode is enabled.

#### Scenario: Redirect to login
- **WHEN** auth mode is enabled and an operator requests the dashboard without a valid session
- **THEN** the system redirects the operator to the login page
