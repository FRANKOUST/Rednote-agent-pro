## Why

The platform needs a collaboration and audit surface outside the core app so teams can review scraped inputs, generated drafts, and publish outcomes. Feishu Bitable sync is the first external collaboration sink and should be implemented separately from generation and publish logic.

## What Changes

- Add Feishu Bitable synchronization for scraped posts, generated drafts, and publish outcomes.
- Support separate tables or views for raw source data and AI-generated content.
- Persist sync records, errors, and idempotency metadata.
- Expose sync status to operators and later automation flows.

## Capabilities

### New Capabilities

- `feishu-bitable-sync`: Synchronization of platform records into Feishu Bitable.
- `sync-record-tracking`: Persistent tracking of sync status, retries, and target identifiers.
- `review-collaboration-export`: Projection of source and generated records into review-friendly external tables.

### Modified Capabilities

None.

## Impact

- Affects Feishu provider adapters, persistence, async workflows, and operational visibility.
- Introduces target schema mapping and idempotent external update requirements.
