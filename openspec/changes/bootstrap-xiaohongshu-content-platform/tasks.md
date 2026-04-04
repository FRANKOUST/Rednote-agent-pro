## 1. Repository and runtime bootstrap

- [ ] 1.1 Create the Python project structure for `app`, `tests`, and shared configuration files.
- [ ] 1.2 Add backend dependencies and local development tooling for FastAPI, SQLAlchemy, Celery, Redis, PostgreSQL, Playwright, and testing.
- [ ] 1.3 Implement the application bootstrap with configuration loading and a health endpoint.

## 2. Persistence and job infrastructure

- [ ] 2.1 Establish the database base model, migration setup, and session management conventions.
- [ ] 2.2 Add queue configuration, worker bootstrap, and a shared async job envelope with status persistence.
- [ ] 2.3 Add storage abstractions and local filesystem-backed implementations for future artifacts.

## 3. Domain and provider contracts

- [ ] 3.1 Define canonical domain entities, value objects, and workflow state enums for drafts, publish jobs, and future source content records.
- [ ] 3.2 Define provider interfaces for LLM, image generation, publisher, and Feishu adapters.
- [ ] 3.3 Add normalized result and error models used across adapters and application services.

## 4. Shared application services and interfaces

- [ ] 4.1 Implement shared application service boundaries for workflow dispatch, status lookup, and validation.
- [ ] 4.2 Add thin REST routes that delegate to shared application services.
- [ ] 4.3 Add initial MCP tool handlers and a minimal Web UI shell that use the same service layer.

## 5. Verification and readiness

- [ ] 5.1 Add unit tests for state rules, provider contract behavior, and input validation.
- [ ] 5.2 Add integration tests for application startup, persistence wiring, and async job dispatch.
- [ ] 5.3 Validate the OpenSpec change and document local startup and test commands for follow-on feature changes.
