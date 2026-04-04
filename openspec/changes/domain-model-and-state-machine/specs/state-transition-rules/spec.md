## ADDED Requirements

### Requirement: Draft lifecycle transitions SHALL be validated
The system SHALL enforce explicit valid transitions for content drafts, including generation, review submission, approval or rejection, publish readiness, and published completion.

#### Scenario: Approve after review
- **WHEN** a draft in `review_pending` receives an approval action
- **THEN** the system transitions it to `approved`

#### Scenario: Reject invalid publish action
- **WHEN** a draft that has not been approved is sent to publish
- **THEN** the system rejects the request instead of forcing an invalid lifecycle transition

### Requirement: Publish jobs SHALL expose terminal-state semantics
The system SHALL distinguish terminal publish job states from in-progress states so retries and dashboards can reason about completion.

#### Scenario: Terminal publish state
- **WHEN** a publish job reaches `published`, `failed`, or `cancelled`
- **THEN** the system marks it as terminal for workflow and UI purposes
