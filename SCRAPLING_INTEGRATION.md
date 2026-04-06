# SCRAPLING Integration

## Provider

- Registry key: `scrapling_xhs`
- Runtime adapter: `app/infrastructure/providers/collector/scrapling_xhs.py`
- Supported collection types: `search`, `detail`

## How it works

1. `PipelineService` or a manual collector run calls the collector provider.
2. The provider chooses fixture/dry-run or live Scrapling fetch mode.
3. The extractor normalizes the fetched page into `SourcePostPayload` objects.
4. The service deduplicates within the run and persists `SourcePost` + `CollectorRun` diagnostics.

## Current safe path

- `XHS_SCRAPLING_MODE=fixture`
- `dry_run=true`
- fixtures under `fixtures/scrapling/`

## Live prerequisites

- `pip install -e .[collectors]`
- `scrapling install`
- valid XHS cookies or storage state
- low-volume operator-controlled usage only

## Diagnostics

Collector diagnostics include mode, retries, attempt count, failure classification, and structured log entries on the `CollectorRun` record.
