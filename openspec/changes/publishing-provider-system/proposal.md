## Why

Publishing requires its own provider boundary and execution records because it is operationally risky and must remain replaceable.

## What Changes

- Add publisher provider interface and default implementation.
- Add publish job records and status transitions.
- Add support for API and browser-automation provider abstraction.

## Capabilities

### New Capabilities

- `publisher-providers`: Replaceable publish providers.
- `publish-job-recording`: Persistent publish attempts and outcomes.

### Modified Capabilities

None.

## Impact

- Controls the last mile of the content pipeline and its operational safety.
