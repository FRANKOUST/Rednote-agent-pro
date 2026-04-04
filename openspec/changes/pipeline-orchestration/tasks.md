## 1. Workflow records

- [ ] 1.1 Keep persisted workflow-run records as the canonical handle for pipeline execution.
- [ ] 1.2 Keep stage and status metadata updated by the application service.

## 2. Dispatcher abstraction

- [ ] 2.1 Keep pipeline execution behind the dispatcher abstraction.
- [ ] 2.2 Preserve at least `inline` and `background` dispatcher modes.

## 3. Verification

- [ ] 3.1 Maintain tests for dispatcher mode behavior.
- [ ] 3.2 Maintain integration tests that prove operator surfaces work against the same workflow-run contract.
