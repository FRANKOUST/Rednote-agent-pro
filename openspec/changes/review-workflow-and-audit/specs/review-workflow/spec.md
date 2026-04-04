## ADDED Requirements

### Requirement: Drafts SHALL require review before publish
The system SHALL require drafts to reach an approved state before publish execution.

#### Scenario: Publish blocked before approval
- **WHEN** an operator attempts to publish a draft that is not approved
- **THEN** the system rejects the request

### Requirement: Draft review actions SHALL be auditable
The system SHALL log approval and rejection actions as audit records.

#### Scenario: Audit draft approval
- **WHEN** a draft is approved
- **THEN** the platform records an audit event for that approval
