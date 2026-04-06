# Provider Integration Matrix

| Capability | Registry Key(s) | Default Mode | Live Requirement | Safety Default | Shared Surface |
|---|---|---|---|---|---|
| Collector | `scrapling_xhs`, `mock`, `playwright` | `scrapling_xhs` in fixture mode | Scrapling fetchers installed + XHS auth state | Fixture / dry-run first | REST + MCP + Web + service |
| Model | `openai_compatible`, `custom_model_router`, `mock` | `custom_model_router` | OpenAI-compatible `base_url` + `api_key` + `model` | Safe fallback to stub/mock | REST + MCP + Web + service |
| Image | `mock`, `openai_compatible` | `mock` | OpenAI-compatible image endpoint + key | Mock first | REST + Web + service |
| Publisher | `mock`, `api`, `browser` | `mock` | Publish credential or browser state | Manual review + live gate | REST + Web + service |
| Sync | `feishu_cli`, `mock` | `feishu_cli` dry-run | Authenticated `lark-cli` plus target Base/Sheet | Dry-run first | REST + MCP + Web + service |

## Notes

- No provider implementation is called directly from route handlers; routes go through `PipelineService`.
- Real external actions are opt-in through env flags and still retain operator-visible diagnostics.
