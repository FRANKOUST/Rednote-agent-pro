## Context

The project now includes runnable code, OpenSpec changes, operator surfaces, tests, and documentation. The canonical `portfolio-packaging` change needs to formalize how the project is presented as a portfolio-grade system rather than a loose collection of implementation artifacts.

Current portfolio assets include:
- project README
- showcase narrative
- demo walkthrough
- architecture and roadmap documents
- repository audit and implementation map

## Goals / Non-Goals

**Goals:**
- Define the required project-storytelling artifacts for a portfolio-ready delivery.
- Keep the portfolio layer honest about mock boundaries versus real integrations.
- Ensure the demo path and architectural value are clear to reviewers.

**Non-Goals:**
- Marketing website generation
- Public launch copywriting or product sales collateral

## Decisions

### Decision: Portfolio docs must reflect the actual implementation state

Portfolio materials SHALL distinguish between implemented mock flows, safe live shells, and true external integrations.

### Decision: Demo docs are part of the deliverable

The project SHALL include a repeatable demo script and showcase narrative so reviewers can understand the system quickly.

## Risks / Trade-offs

- [Portfolio docs can drift from the code] → Keep showcase and README updates tied to implementation milestones.
- [Overclaiming real integrations would weaken credibility] → Explicitly label mock providers, safe stubs, and live-shell boundaries.

## Migration Plan

1. Preserve and update the current showcase and demo docs.
2. Expand the portfolio package when new real integrations land.

## Open Questions

- Which screenshots or recorded demos should be added once the operator console stabilizes further?
