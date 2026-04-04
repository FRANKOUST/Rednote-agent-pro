## ADDED Requirements

### Requirement: The platform SHALL support replaceable sync providers
The system SHALL select sync providers through configuration, supporting safe stubs and live shells.

#### Scenario: Configure Feishu sync
- **WHEN** Feishu is selected as the sync provider
- **THEN** the platform uses the configured Feishu sync path with safe fallback when necessary
