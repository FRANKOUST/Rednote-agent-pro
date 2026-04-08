# SHOWCASE

## 作品集展示角度

本项目适合作为“AI + 内容运营 + 平台产品化 + 工程治理”综合作品展示：

- 有真实业务阶段：采集、分析、选题、写作、配图、审核、发布、同步
- 有统一业务层：REST / MCP / Web 共用
- 有 provider registry 与安全兜底
- 有发布 safety gate 与 sync 业务语义
- 有 operator-facing schema / prompt templates / diagnostics

## 最值得展示的页面 / 动作

- `/` 内容助手工作台
- `/console/runs/{run_id}` Pipeline Run 详情
- `/console/runs/{run_id}/diagnostics` Stage Diagnostics
- `/console/providers` Provider Status + Login Checks
- MCP `run_content_pipeline` / `prepare_publish` / `sync_generated_data`

## 最能说明工程质量的点

- 两阶段采集不是写死在 route 或页面层，而是在 collector provider 内部完成
- 发布与同步不是单个“底层动作”，而是完整的运营语义
- prompt 版本化、schema-first、provider-agnostic
- 默认 dry-run、默认人工审核、保留 safety gate
- 全量测试通过
