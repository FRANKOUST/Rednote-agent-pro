# System Blueprint

## 1. Pipeline Orchestration

主流程采用阶段化编排：

1. `crawl`
2. `analyze`
3. `generate_topics`
4. `generate_drafts`
5. `generate_images`
6. `review_gate`
7. `publish`
8. `sync_feishu`

阶段之间通过持久化产物衔接，而不是依赖内存链式对象。每个阶段都可以单独重试、观测和回放。

## 2. Failure Recovery and Retry

- `crawl` 失败：记录 provider、页面、选择器、认证状态
- `analyze` / `generate` 失败：记录模型、prompt、retryable 标记
- `publish` 失败：记录通道、最后成功步骤、fallback 是否触发
- `sync` 失败：记录目标系统、实体类型、幂等键

恢复策略：

- 允许从失败阶段继续
- 保留部分成功结果
- 区分 `retryable` 与 `non_retryable`

## 3. Review and Rollback

- 默认人工审核
- 审核通过后才允许进入 `publish_ready`
- 发布前仍执行完整性检查
- 驳回后保留 draft 与审计记录
- 已发布内容的后续撤回不放进 phase one 实现，但保留 publish provider 扩展点

## 4. Provider Abstraction

Provider 全部通过内部契约访问：

- `CollectorProvider`
- `LanguageModelProvider`
- `ImageProvider`
- `PublisherProvider`
- `SyncProvider`

业务层永远不直接依赖第三方 SDK 返回结构。

## 5. REST API Design

核心接口：

- `POST /api/pipeline-runs`
- `GET /api/pipeline-runs/{id}`
- `GET /api/drafts`
- `POST /api/drafts/{id}/approve`
- `POST /api/drafts/{id}/reject`
- `POST /api/drafts/{id}/publish`
- `GET /api/publish-jobs`
- `GET /api/sync-records`
- `GET /api/audit-logs`

## 6. MCP Tools Design

phase-one 采用轻量 JSON-RPC tool surface：

- `tools/list`
- `tools/call`

核心 tool：

- `start_pipeline`
- `list_drafts`
- `list_publish_jobs`

后续可扩展：

- `approve_draft`
- `publish_draft`
- `get_run`

## 7. Web Console Information Architecture

首页承担 3 个职责：

- 发起 pipeline
- 查看 draft 队列
- 查看最近审计日志

后续页面建议拆分：

- `Runs`
- `Draft Review`
- `Publish Records`
- `Sync Records`
- `Provider Health`

## 8. Database Design

当前表：

- `workflow_runs`
- `source_posts`
- `analysis_reports`
- `topic_suggestions`
- `content_drafts`
- `image_assets`
- `publish_jobs`
- `sync_records`
- `audit_logs`

设计原则：

- 业务实体与操作记录分离
- 内容状态与发布状态分离
- 审计日志独立建模

## 9. Queue and Task Model

phase-one 采用抽象化任务派发，默认本地 `inline` 执行，保证 demo 可直接跑通。

演进方向：

- `inline dispatcher` -> `Redis/Celery/RQ` -> 更强工作流引擎

接口层不能感知底层调度实现。

## 10. Configuration Management

使用 `pydantic-settings` 和 `.env`：

- app 基本信息
- database URL
- media directory
- task mode
- allow auto publish
- default providers

## 11. Logging, Monitoring, Audit

phase-one 已实现审计日志持久化。

后续增强：

- 结构化应用日志
- 任务级 trace id
- provider latency
- stage duration
- dashboard metrics

## 12. Permission Boundary

当前定位是单团队内部使用。

phase-one 边界：

- 不做多租户
- 不做复杂 RBAC
- 通过部署边界和默认关闭高风险 provider 控制风险

## 13. Deployment Design

本地 demo：

- SQLite
- 本地 media 目录
- `uvicorn app.main:app --reload`

后续部署：

- PostgreSQL
- Redis/Celery
- Playwright runtime
- provider credentials via secret manager

## 14. Evolution Roadmap

1. 用真实 collector 替换 mock collector
2. 用真实 LLM / image provider 替换 mock provider
3. 接入真实 publish API 与 browser automation fallback
4. 接入真实 Feishu Bitable
5. 增强 MCP 兼容性
6. 强化 observability 与 operator auth
