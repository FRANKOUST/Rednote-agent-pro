# Provider Integration Matrix

| Capability | Mock | Safe Stub | Live Shell | Real Validation Complete |
|---|---|---|---|---|
| Collector | Yes | Safe Playwright fallback | Safe Playwright live shell | No |
| Analysis LLM | Yes | OpenAI safe stub | OpenAI live HTTP shell | No |
| Draft LLM | Yes | OpenAI safe stub | OpenAI live HTTP shell | No |
| Image Generation | Yes | OpenAI safe stub | OpenAI image live shell | No |
| Publish API | Yes | API safe stub | API live HTTP shell | No |
| Publish Browser | Yes | Browser safe stub | Browser live Playwright shell | No |
| Sync / Feishu | Yes | Feishu safe stub | Feishu live HTTP shell | No |

## Notes

- "Live Shell" means the code path exists and attempts a real integration before falling back safely.
- "Real Validation Complete" requires real credentials, approved accounts, and a recorded validation run.
