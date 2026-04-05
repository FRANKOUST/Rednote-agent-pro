# Acceptance Checklist

## Platform

- [x] App starts locally
- [x] SQLite local mode works
- [x] REST, MCP, and Web Console share the same business layer

## Workflow

- [x] Main pipeline runs end to end in mock mode
- [x] Draft review is required before publish
- [x] Publish jobs are persisted
- [x] Sync records are persisted
- [x] Audit logs are persisted

## Safety

- [x] Auth can protect REST and MCP
- [x] Web Console login exists
- [x] Basic role separation exists for viewer/operator/reviewer/admin
- [x] Live publish gate defaults to safe behavior
- [x] Provider fallback paths exist

## Observability

- [x] Request IDs are attached
- [x] Run diagnostics are queryable
- [x] Provider diagnostics are queryable
- [x] Provider health is queryable

## Provider Paths

- [x] Mock providers exist
- [x] Safe stubs exist
- [x] Live shells exist
- [ ] Real credentials validated in production-like conditions

## Worker Execution

- [x] Inline mode
- [x] Background mode
- [x] Worker stub mode
- [x] External worker adapter mode
- [x] Inspect / cancel / requeue controls
- [x] Dead-letter-like handling
- [ ] Durable distributed queue backend

## Operator Experience

- [x] Dashboard
- [x] Entity list view
- [x] Source post detail page
- [x] Analysis report detail page
- [x] Topic suggestion detail page
- [x] Image asset detail page
- [x] Run detail and diagnostics page
- [x] Publish history
- [x] Sync history
- [x] Diagnostics visibility

## Validation

- [x] Test suite passes
- [ ] Real collector validation run recorded
- [ ] Real model validation run recorded
- [ ] Real sync validation run recorded
- [ ] Real publish or safe dry-run publish validation recorded
