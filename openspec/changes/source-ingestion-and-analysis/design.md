## Context

The current implementation persists source posts, analysis reports, and topic suggestions through the shared pipeline service. Collection can run through mock data or the safe Playwright collector shell, while analysis and topic generation can run through mock or OpenAI-backed provider selections.

## Goals / Non-Goals

**Goals:**
- Formalize source ingestion, analysis reporting, and topic suggestion generation.
- Preserve traceability from collected posts to reports and topics.
- Keep the collector and model layers replaceable.

**Non-Goals:**
- Full real-world DOM selector hardening
- Deep comment or author-profile crawling

## Decisions

### Decision: Source ingestion remains provider-based

Collector execution SHALL remain behind a collector provider boundary, with safe Playwright behavior and mock fallback.

### Decision: Analysis and topic generation remain evidence-backed

Analysis reports and topic suggestions SHALL be persisted separately so later generation stages can reference them explicitly.

## Risks / Trade-offs

- [Real source pages are unstable] → Keep the safe collector fallback and diagnostics.
- [Model outputs can vary] → Preserve report and topic persistence rather than treating them as transient intermediates.

## Migration Plan

1. Keep current persisted entity boundaries.
2. Improve real collector and real model providers in follow-on iterations.

## Open Questions

- Which extracted source-post fields should become first-class for future ranking or filtering?
