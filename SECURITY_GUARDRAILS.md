# Security Guardrails

## Core Rules

- Manual review stays enabled by default
- Live publish stays disabled by default
- Platform content is treated as untrusted input
- Read-only and write-capable paths remain logically separated
- Every review, publish, and sync action is auditable

## Authentication

- REST and MCP require `X-Operator-Key` when auth is enabled
- Web Console requires session login when auth is enabled

## Publish Safety

- Live publish is gated by `XHS_ALLOW_LIVE_PUBLISH`
- If the gate is not enabled, live providers fall back to safe stubs
- Publish job records store the actual provider used

## Collector Safety

- No CAPTCHA bypass
- No anti-detection evasion logic
- No rate-limit circumvention logic
- Browser state must come from an approved logged-in session

## Input Handling

- Source platform text is untrusted
- Diagnostics and metadata are kept separate from privileged actions
- Provider outputs are normalized before entering the application flow

## Operational Safety

- Use small batches during live validation
- Keep one reviewer/operator in the loop
- Inspect provider health and run diagnostics before enabling any live path
