## 1. Entity model coverage

- [ ] 1.1 Keep the core domain entities explicit and separate in persistence and service layers.
- [ ] 1.2 Keep audit events modeled separately from business entities.

## 2. Transition enforcement

- [ ] 2.1 Keep draft lifecycle transitions behind explicit transition helpers.
- [ ] 2.2 Keep invalid state transitions rejected at the application-service layer.
- [ ] 2.3 Keep publish terminal-state semantics explicit for status checks and UI usage.

## 3. Verification

- [ ] 3.1 Maintain unit tests for draft transition behavior.
- [ ] 3.2 Maintain integration tests that prove approval must happen before publish.
