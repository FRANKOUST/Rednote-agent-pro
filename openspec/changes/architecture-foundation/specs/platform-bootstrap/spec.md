## ADDED Requirements

### Requirement: Application bootstrap SHALL initialize the platform runtime
The system SHALL provide a single application bootstrap that loads configuration, initializes persistence, and registers all operator-facing routers.

#### Scenario: Startup in local mode
- **WHEN** the application starts with the default local configuration
- **THEN** it initializes the database, loads settings, and exposes the configured REST, MCP, and Web routes

### Requirement: Local runtime SHALL be low-friction by default
The system SHALL support a local demo mode that runs with SQLite and filesystem-backed media storage without requiring external infrastructure.

#### Scenario: Zero-infrastructure local startup
- **WHEN** a developer starts the app with the documented local configuration
- **THEN** the platform runs successfully without requiring PostgreSQL, Redis, or external providers
