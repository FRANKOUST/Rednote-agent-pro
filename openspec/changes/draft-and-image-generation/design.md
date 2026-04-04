## Context

The platform already generates content drafts and image assets during the main pipeline. Drafts and images are persisted and exposed through entity APIs.

## Goals / Non-Goals

**Goals:**
- Formalize draft and image generation as separate persisted stages.
- Preserve provider abstraction for LLM and image generation.

**Non-Goals:**
- Rich creative editing workflows
- Multi-image bundle generation

## Decisions

### Decision: Drafts remain structured records

Drafts SHALL include title, body, tags, CTA, image prompt, and content type as explicit fields.

### Decision: Image assets remain persisted files

Generated image assets SHALL be persisted to local storage in phase one, behind an image-provider abstraction.

## Risks / Trade-offs

- [Real image generation can be expensive] → Keep safe fallbacks and local mock image generation.
- [Draft structure may need to evolve] → Preserve explicit fields and extend incrementally.

## Migration Plan

1. Keep current persisted draft and image entity shapes.
2. Improve real image/model behavior through provider swaps.

## Open Questions

- Should future image support include multiple renditions per draft?
