## Why

The product's value depends on turning validated topic ideas into publishable draft assets rather than stopping at research. Draft and image generation must be independent capabilities so the team can iterate on prompt quality, provider selection, and output structure without entangling review or publish logic.

## What Changes

- Add AI-generated content drafts for each selected topic.
- Generate title, body, hashtag set, CTA, content type, and image guidance for each draft.
- Integrate `gpt-image-1` as the initial image provider and save generated images locally.
- Persist draft and image assets with provider metadata and traceable generation inputs.

## Capabilities

### New Capabilities

- `content-draft-generation`: AI generation of structured Xiaohongshu draft variants from approved topics.
- `image-asset-generation`: Image generation and local asset persistence for platform drafts.
- `generation-audit-trace`: Prompt, provider, parameter, and output traceability for generated content and images.

### Modified Capabilities

None.

## Impact

- Affects model provider adapters, local asset storage, persistence, and review-stage inputs.
- Introduces larger payload storage and stricter output schema validation requirements.
