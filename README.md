# Xiaohongshu Content Platform

一个面向单团队内部使用的“小红书内容挖掘与自动生成系统”工程样板，采用 `FastAPI + SQLAlchemy + Provider 插件层 + 可演进异步任务编排`，覆盖从内容采集、爆款分析、选题生成、文案生成、配图生成，到人工审核、发布记录、同步记录和操作台管理的完整闭环。

当前仓库不是“只会调模型的 demo”，而是一个具备以下特征的平台雏形：

- 有清晰的领域模型与状态机
- 有 OpenSpec 变更管理结构
- 有 oh-my-codex 实施计划与工程文档
- 有可运行的后端主流程
- 有 REST API、MCP-style tool server、Web Console 三种入口
- 有 mock provider、safe stub、live shell 三层 provider 演进路径
- 有基础 auth、observability、diagnostics、audit、sync 记录
- 有外部 worker adapter 的演进位点

## 1. 项目目标

这个项目的目标不是只做一条脚本式自动化流水线，而是构建一个可持续演进的平台：

1. 从小红书竞品内容中采集结构化内容样本
2. 分析高频关键词、标签、标题模式和用户洞察
3. 基于分析结果生成选题
4. 基于选题生成文案草稿和配图
5. 进入人工审核流
6. 审核通过后创建发布任务
7. 将关键阶段结果同步到协作系统
8. 支持人类操作员和 AI agent 通过不同入口调用同一业务层

## 2. 当前实现状态

当前版本已经是一个**可运行、可测试、可演示、可写进作品集**的阶段性交付，不再是空仓库或纸面设计。

### 已完成

- 模块化单体后端骨架
- 核心领域实体与状态机
- SQLite 本地持久化
- 主链路跑通：
  - `crawl -> analyze -> topic -> draft -> image -> review -> publish -> sync`
- REST API
- 实体级 REST API
- MCP-style tool server
- MCP 实体查询与详情工具
- Web Console
- Web Console 登录与 session 保护
- 审核流
- 发布记录
- 同步记录
- 审计日志
- request-id、run diagnostics、provider diagnostics、provider health
- dispatcher：
  - `inline`
  - `background`
  - `worker_stub`
  - `external_worker`
- external worker adapter：
  - `filesystem`
  - `subprocess`
- provider 三层演进模型：
  - `mock`
  - `safe stub`
  - `live shell`

### 未完成但已预留位点

- 真实小红书 Playwright 采集选择器与登录态验证
- 真实 OpenAI 文本/图像调用结果的结构化消费
- 真实 Feishu Bitable 字段映射与幂等更新
- 真实 API 发布与浏览器自动发布的生产验证
- durable queue / distributed worker backend

## 3. 核心能力概览

### 3.1 数据采集

当前支持两类采集 provider：

- `mock-collector`
- `safe-playwright-collector`

`safe-playwright-collector` 已具备真实浏览器导航壳层，但在缺少浏览器依赖、storage state、运行权限或发生异常时，会自动回退到 mock/fallback 路径，不会直接把整个 pipeline 打死。

### 3.2 数据分析与选题

当前通过 LLM provider 层完成：

- source posts -> analysis report
- analysis report -> topic suggestions

支持：

- mock LLM
- OpenAI safe stub
- OpenAI live shell

### 3.3 草稿与配图生成

当前可生成：

- 标题
- 正文
- 标签
- CTA
- 图片提示词
- 内容类型

图像生成支持：

- mock image provider
- OpenAI safe stub
- OpenAI live shell

### 3.4 审核与发布

核心规则：

- 默认必须人工审核
- draft 必须 `approved` 才能进入发布
- live publish 默认关闭
- 即使配置了 live publish provider，若未显式开启 `allow_live_publish`，也会强制回退到 safe stub

### 3.5 同步与审计

当前已持久化：

- source post batch sync
- content draft batch sync
- publish job sync
- audit logs

## 4. 架构设计

总体架构：

- 模块化单体
- Provider 插件层
- 共享应用服务层
- 可演进任务调度抽象

### 分层

#### Interface Layer

- REST
- MCP
- Web Console

#### Application Layer

- pipeline orchestration
- review flow
- publish orchestration
- sync orchestration

#### Domain Layer

- state machines
- DTOs / payloads
- provider contracts

#### Infrastructure Layer

- database
- mock providers
- safe stubs
- live shells
- external worker adapters

## 5. 核心领域模型

系统围绕以下实体建模：

- `SourcePost`
- `AnalysisReport`
- `TopicSuggestion`
- `ContentDraft`
- `ImageAsset`
- `PublishJob`
- `SyncRecord`
- `AuditLog`
- `WorkflowRun`
- `WorkflowStageEvent`

### Draft 状态机

`created -> generated -> review_pending -> approved / rejected -> publish_ready -> published`

### PublishJob 状态机

`queued -> preparing -> publishing -> published / failed / cancelled`

## 6. 目录结构

```text
app/
  application/
    dispatcher.py
    external_worker.py
    factory.py
    services.py
    worker_runner.py
  core/
    config.py
    middleware.py
  db/
    base.py
    models.py
    session.py
  domain/
    contracts.py
    models.py
  infrastructure/
    providers/
      collector/
      llm/
      image/
      publisher/
      feishu/
      registry.py
  interfaces/
    rest/
      routes.py
    mcp/
      routes.py
    web/
      routes.py
  main.py
templates/
  index.html
  login.html
  entities.html
  entity_detail.html
tests/
  unit/
  integration/
docs/
  portfolio/
  superpowers/
openspec/
```

## 7. 配置说明

主要配置来自 `.env`。

参考文件：

- [.env.example](G:\projects\tests\test\.env.example)

重要配置项：

- `XHS_DATABASE_URL`
- `XHS_MEDIA_DIR`
- `XHS_TASK_MODE`
- `XHS_DEFAULT_COLLECTOR_PROVIDER`
- `XHS_DEFAULT_MODEL_PROVIDER`
- `XHS_DEFAULT_IMAGE_PROVIDER`
- `XHS_DEFAULT_PUBLISH_PROVIDER`
- `XHS_DEFAULT_SYNC_PROVIDER`
- `XHS_ENABLE_REAL_COLLECTOR`
- `XHS_ENABLE_REAL_MODEL_PROVIDER`
- `XHS_ENABLE_REAL_IMAGE_PROVIDER`
- `XHS_ENABLE_REAL_PUBLISH_PROVIDER`
- `XHS_ENABLE_REAL_SYNC_PROVIDER`
- `XHS_ALLOW_LIVE_PUBLISH`
- `XHS_AUTH_ENABLED`
- `XHS_OPERATOR_API_KEY`
- `XHS_WORKER_ADAPTER_KIND`
- `XHS_WORKER_QUEUE_DIR`
- `XHS_OPENAI_API_KEY`
- `XHS_FEISHU_APP_ID`
- `XHS_FEISHU_APP_SECRET`
- `XHS_XHS_PUBLISH_API_BASE`
- `XHS_XHS_PUBLISH_API_TOKEN`

## 8. Provider 模型

每类外部能力都遵循同一演进路径：

1. `mock`
2. `safe stub`
3. `live shell`

### 例子

#### LLM

- `mock-llm`
- `openai-safe-llm-stub`
- `openai-live-llm`

#### Image

- `mock-image`
- `openai-safe-image-stub`
- `openai-live-image`

#### Publish

- `mock-publisher`
- `xhs-api-safe-stub`
- `xhs-api-live-publisher`
- `xhs-browser-safe-stub`
- `xhs-browser-live-publisher`

#### Sync

- `mock-feishu`
- `feishu-safe-stub`
- `feishu-live-sync`

#### Collector

- `mock-collector`
- `safe-playwright-collector`

## 9. 运行模式

### 9.1 本地演示模式

推荐默认使用：

- SQLite
- local media directory
- mock / safe provider
- `inline` task mode

### 9.2 背景任务模式

当前支持：

- `inline`
- `background`
- `worker_stub`
- `external_worker`

### 9.3 external worker adapter

当前可用适配器：

- `filesystem`
- `subprocess`

`filesystem` 会写入任务 manifest。  
`subprocess` 会在本地启动独立 Python 进程执行 manifest 对应任务。

这仍然不是最终 durable queue，但已经是从 demo 走向真实 worker 的有效过渡层。

## 10. 安全边界

### 10.1 Operator Auth

当 `XHS_AUTH_ENABLED=true` 时：

- REST / MCP 需要 `X-Operator-Key`
- Web Console 需要登录并获得 session cookie

### 10.2 Live Publish Gate

即使你启用了 live publish provider：

- 若 `XHS_ALLOW_LIVE_PUBLISH=false`
- 系统仍然会强制回退到 safe stub

### 10.3 Safe Fallback

以下情况都会自动回退：

- 缺少 API key
- 缺少 Feishu 凭证
- 缺少 publish token
- Playwright 不可用
- 缺少 browser storage state
- 远程请求失败
- 浏览器自动化失败

## 11. 快速启动

### Windows / PowerShell

1. 安装依赖

```powershell
pip install -e .[dev]
```

2. 复制环境变量模板

```powershell
copy .env.example .env
```

3. 启动服务

```powershell
uvicorn app.main:app --reload
```

4. 打开以下入口

- Web Console: `http://127.0.0.1:8000/`
- OpenAPI: `http://127.0.0.1:8000/docs`
- MCP-style endpoint: `http://127.0.0.1:8000/mcp`

## 12. Web Console 演示路径

### Dashboard

- `/`

你可以：

- 发起 pipeline run
- 查看 runs
- 查看 drafts
- 审核 draft
- 发布 draft
- 查看 publish jobs
- 查看 sync records
- 查看 audit logs
- 查看 provider diagnostics / provider health

### Entity View

- `/console/entities`

当前可查看：

- Source Posts
- Analysis Reports
- Topic Suggestions
- Image Assets

### Entity Detail

当前已支持 detail page：

- `/console/source-posts/{id}`
- `/console/analysis-reports/{id}`
- `/console/topic-suggestions/{id}`
- `/console/image-assets/{id}`
- `/console/runs/{id}`
- `/console/runs/{id}/diagnostics`

## 13. REST API 概览

### Workflow

- `POST /api/pipeline-runs`
- `GET /api/pipeline-runs`
- `GET /api/pipeline-runs/{id}`
- `GET /api/pipeline-runs/{id}/diagnostics`

### Draft

- `GET /api/drafts`
- `POST /api/drafts/{id}/approve`
- `POST /api/drafts/{id}/reject`
- `POST /api/drafts/{id}/publish`

### Entity APIs

- `GET /api/source-posts`
- `GET /api/source-posts/{id}`
- `GET /api/analysis-reports`
- `GET /api/analysis-reports/{id}`
- `GET /api/topic-suggestions`
- `GET /api/topic-suggestions/{id}`
- `GET /api/image-assets`
- `GET /api/image-assets/{id}`

### Ops / Audit / Sync

- `GET /api/publish-jobs`
- `GET /api/sync-records`
- `GET /api/audit-logs`
- `GET /api/observability/summary`
- `GET /api/providers/diagnostics`
- `GET /api/providers/health`
- `GET /api/health`

## 14. MCP Tool Surface

当前支持工具包括：

- `start_pipeline`
- `list_runs`
- `list_drafts`
- `list_publish_jobs`
- `list_source_posts`
- `list_analysis_reports`
- `list_topic_suggestions`
- `list_image_assets`
- `get_source_post`
- `get_analysis_report`
- `get_topic_suggestion`
- `get_image_asset`

## 15. 示例调用

### 启动 pipeline

```powershell
curl -X POST http://127.0.0.1:8000/api/pipeline-runs `
  -H "Content-Type: application/json" `
  -d "{\"keywords\":[\"咖啡\"],\"min_likes\":100,\"auto_publish\":false}"
```

### 查询 entity API

```powershell
curl http://127.0.0.1:8000/api/source-posts
curl http://127.0.0.1:8000/api/analysis-reports
curl http://127.0.0.1:8000/api/topic-suggestions
curl http://127.0.0.1:8000/api/image-assets
```

### MCP tools/list

```powershell
curl -X POST http://127.0.0.1:8000/mcp `
  -H "Content-Type: application/json" `
  -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}"
```

### MCP tools/call

```powershell
curl -X POST http://127.0.0.1:8000/mcp `
  -H "Content-Type: application/json" `
  -d "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/call\",\"params\":{\"name\":\"start_pipeline\",\"arguments\":{\"keywords\":[\"护肤\"],\"auto_publish\":false}}}"
```

## 16. 测试

运行：

```powershell
pytest -q
```

当前结果：

- `53 passed`

测试覆盖重点：

- 状态机
- provider registry
- live provider fallback
- safe Playwright fallback
- external worker adapter
- REST 主链路
- MCP tool surface
- auth / observability
- Web Console entity 视图

## 17. 文档与规范

关键文档：

- [repository audit](G:\projects\tests\test\docs\superpowers\specs\2026-04-04-repository-audit.md)
- [system blueprint](G:\projects\tests\test\docs\superpowers\specs\2026-04-04-system-blueprint.md)
- [canonical change map](G:\projects\tests\test\docs\superpowers\specs\2026-04-04-canonical-change-map.md)
- [implementation map](G:\projects\tests\test\docs\superpowers\plans\2026-04-04-implementation-map.md)
- [portfolio showcase](G:\projects\tests\test\docs\portfolio\SHOWCASE.md)
- [demo script](G:\projects\tests\test\docs\portfolio\DEMO.md)

OpenSpec canonical changes 已覆盖：

- architecture-foundation
- domain-model-and-state-machine
- pipeline-orchestration
- source-ingestion-and-analysis
- draft-and-image-generation
- review-workflow-and-audit
- publishing-provider-system
- feishu-sync
- rest-api
- mcp-server
- web-console
- testing-observability-and-devex
- portfolio-packaging

## 18. 已知边界

当前版本默认优先：

- 本地可运行
- 主链路可演示
- 架构边界清晰
- provider 可替换
- 真实 provider 有安全降级

当前仍未声称完成：

- 真实小红书平台集成验证
- 真实 Feishu Bitable 字段映射验证
- 真实 OpenAI 返回格式在生产环境下的鲁棒消费
- durable distributed queue backend

## 19. 后续扩展建议

下一步适合做的方向：

1. 验证 live shells 的真实凭证路径
2. 增加 durable queue / worker backend
3. 增加实体 detail 的 MCP / Web 深化体验
4. 增加更细粒度的 provider health 与 metrics
5. 增加 Web Console 的 review / publish / diagnostics 专页

## 20. 这个项目适合展示什么

如果你把它放进作品集，这个项目最适合突出：

- 平台化系统设计能力
- provider abstraction 能力
- 内容生产工作流建模能力
- 人工审核与自动化能力并存的安全设计
- agent interface 与 human interface 复用同一业务层的工程能力
- 从规范、设计、实施计划到代码和测试的完整闭环能力
