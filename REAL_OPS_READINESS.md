# Real Ops Readiness

## Purpose

This document defines whether the project is ready for small-scale real operation under controlled conditions.

## Current Readiness Level

Status: **Conditionally ready for controlled small-scale validation**

Meaning:

- The platform is operationally ready for supervised runs using safe defaults.
- Real integrations are wired and can be validated once credentials and approved accounts are available.
- The system is not configured for unattended mass automation.

## What Is Ready

- Controlled pipeline execution
- Manual review before publish
- Live-publish safety gate
- Run, stage, sync, publish, and audit persistence
- Provider diagnostics and health checks
- REST, MCP, and Web operator entrypoints
- External worker adapters for local small-scale execution

## What Still Requires Real Validation

- Real authenticated Xiaohongshu browser sessions
- Real OpenAI responses under production prompts and schemas
- Real Feishu table mappings and idempotent updates
- Real publish provider permissions and platform-side behavior

## Safe Operating Constraints

- Keep `XHS_ALLOW_LIVE_PUBLISH=false` by default
- Use small keyword batches
- Use one operator session at a time during validation
- Review every generated draft manually
- Capture all validation runs in the validation report

## Minimum Requirements Before Enabling Live Validation

- Approved account/session for collector
- Approved account/session for browser publish if used
- Valid OpenAI API key
- Valid Feishu app credentials
- Operator on duty to review outputs and inspect diagnostics
