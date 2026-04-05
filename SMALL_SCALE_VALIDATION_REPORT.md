# Small Scale Validation Report

## Status

Current status: **pre-credential validation complete**

Meaning:

- All non-credential engineering work for small-scale validation is in place.
- Remaining validation steps require real credentials, approved accounts, and controlled live test runs.

## Completed Validation

- Mock end-to-end pipeline
- Review / publish / sync lifecycle
- Provider fallback behavior
- Auth and operator controls
- External worker adapter execution
- Entity-level REST and MCP access
- Web Console operator flow
- Model output schema validation
- Prompt template versioning
- Regeneration / revision flow for rejected drafts
- Dead-letter-like worker failure handling

## Pending Live Validation

### Collector

- Real logged-in browser session
- Controlled small keyword batch
- Validation of extracted fields against page reality

### Model

- Real OpenAI key
- Structured output quality checks on real samples
- Prompt-output error analysis

### Publish

- Approved low-risk account or dry-run proxy target
- Manual pre-publish confirmation
- Post-publish status verification

### Sync

- Real Feishu app credentials
- Real table schema mapping
- Upsert / retry verification

## Required Inputs To Finish Live Validation

- OpenAI API key
- Feishu app credentials
- Xiaohongshu-approved session state and/or publish credentials
- Approved live-validation target accounts/environments

## Conclusion

The remaining work needed for full real small-scale validation is now external rather than architectural:

- provider credentials
- approved platform sessions and accounts
- safe live test targets
