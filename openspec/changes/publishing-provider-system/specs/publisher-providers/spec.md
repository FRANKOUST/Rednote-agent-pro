## ADDED Requirements

### Requirement: The platform SHALL support replaceable publish providers
The system SHALL select publish providers through configuration and preserve API and browser provider modes.

#### Scenario: Select browser provider
- **WHEN** browser publish is configured
- **THEN** the platform uses the browser publish provider path

### Requirement: Live publish SHALL be safety-gated
The system SHALL fall back to safe publish stubs unless live publish is explicitly allowed.

#### Scenario: Force safe stub
- **WHEN** a live publish provider is configured but live publish is not allowed
- **THEN** the platform executes a safe publish stub instead
