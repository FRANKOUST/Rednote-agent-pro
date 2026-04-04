## ADDED Requirements

### Requirement: External integrations SHALL use provider contracts
The system SHALL access LLM, image generation, publisher, and Feishu integrations through internal provider interfaces rather than directly from application services.

#### Scenario: Provider swap safety
- **WHEN** a new vendor implementation is added for an existing capability
- **THEN** the application layer can select that vendor without changing its core business logic

### Requirement: Provider outputs SHALL be normalized
The system SHALL convert provider-specific responses into internal data transfer objects or domain models before application services consume them.

#### Scenario: Normalized generation result
- **WHEN** a content generation provider returns vendor-specific fields
- **THEN** the adapter maps them into a stable internal result shape before returning control to the application layer

### Requirement: Provider errors SHALL be adapter-scoped
The system SHALL translate vendor-specific failures into internal error categories that preserve actionable context without leaking raw SDK assumptions into domain logic.

#### Scenario: Publish provider failure normalization
- **WHEN** a publisher adapter encounters a provider-specific failure
- **THEN** it returns an internal error classification with actionable context for retry or fallback decisions
