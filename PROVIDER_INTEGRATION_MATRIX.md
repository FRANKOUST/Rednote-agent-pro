# PROVIDER_INTEGRATION_MATRIX

| Provider Domain | Current Path | Default Mode | Real Validation Needed |
|---|---|---|---|
| Collector | `mock` / `scrapling_xhs` / `playwright` | fixture / safe fallback | XHS storage state or cookies |
| Model | `mock` / `custom_model_router` / `openai_compatible` | mock-safe | OpenAI-compatible endpoint |
| Image | `mock` / `openai_compatible` | mock-safe | image endpoint |
| Publisher | `mock` / `api_safe_stub` / `browser_safe_stub` / live variants | safe preview first | publish token or browser state |
| Sync | `mock` / `feishu_cli` | dry-run first | `lark-cli` login + target permission |

## 统一约束

- 所有入口都必须走统一 service layer
- provider 只负责能力实现，不承载 route / UI 逻辑
- diagnostics / health / login check 需要可独立查看
- 所有 live path 都必须有 safe fallback
