## ADDED Requirements

### Requirement: The codebase SHALL preserve modular package boundaries
The system SHALL separate configuration, domain rules, persistence, provider implementations, application services, and interface handlers into distinct package areas.

#### Scenario: Shared service reuse
- **WHEN** a workflow capability is exposed through multiple interfaces
- **THEN** those interfaces delegate to shared application services instead of reimplementing business logic

### Requirement: Provider selection SHALL be centralized
The system SHALL resolve provider implementations through a central registry driven by configuration.

#### Scenario: Provider lookup
- **WHEN** the application service needs a collector, model, image, publisher, or sync adapter
- **THEN** it obtains the adapter from the configured registry instead of constructing provider implementations inline
