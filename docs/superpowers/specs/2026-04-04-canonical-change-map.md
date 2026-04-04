# Canonical OpenSpec Change Map

## architecture-foundation

- Goal: 建立模块化单体骨架、配置、数据库与接口分层
- Scope: app bootstrap、settings、persistence base、shared wiring
- Non-goals: 真实业务能力
- Key decisions: local demo 默认 SQLite；服务层共享给 REST/MCP/Web
- Acceptance: 应用可启动、数据库初始化、基础健康检查可用
- Risks: 过度设计
- Dependencies: none

## domain-model-and-state-machine

- Goal: 固化核心实体与状态机
- Scope: SourcePost、AnalysisReport、TopicSuggestion、ContentDraft、ImageAsset、PublishJob、SyncRecord
- Non-goals: 真实 provider 接入
- Key decisions: 内容状态与发布状态分离
- Acceptance: 状态流转可测试
- Risks: 单字段状态不足以表达复杂流程
- Dependencies: architecture-foundation

## pipeline-orchestration

- Goal: 建立阶段化任务编排与可恢复执行模型
- Scope: workflow runs、stage transitions、error capture
- Non-goals: 重型工作流引擎
- Key decisions: 先用 dispatcher abstraction，本地默认 inline
- Acceptance: pipeline 可被创建、执行、查询
- Risks: demo 调度与生产调度之间存在差距
- Dependencies: architecture-foundation, domain-model-and-state-machine

## source-ingestion-and-analysis

- Goal: 实现内容采集与爆款规律分析
- Scope: collector provider、source post persistence、analysis report、topic suggestions
- Non-goals: 发布与同步
- Key decisions: mock provider 先跑通，再替换 Playwright 和真实模型
- Acceptance: 能生成 source posts、analysis report、topics
- Risks: 真实页面结构变化大
- Dependencies: architecture-foundation, domain-model-and-state-machine, pipeline-orchestration

## draft-and-image-generation

- Goal: 基于 topic 生成 drafts 和 image assets
- Scope: draft generation、image generation、generation trace
- Non-goals: 最终发布
- Key decisions: provider 输出统一归一化
- Acceptance: drafts 和 images 可生成并持久化
- Risks: 真实图片 provider 成本与延迟
- Dependencies: source-ingestion-and-analysis

## review-workflow-and-audit

- Goal: 实现人工审核、驳回、发布前门禁和审计
- Scope: approve/reject/publish_ready、audit logs
- Non-goals: 多级审批
- Key decisions: 默认人工审核；所有关键动作写审计日志
- Acceptance: 审核状态流转可见、可验证
- Risks: 审核粒度后续可能扩展
- Dependencies: draft-and-image-generation

## publishing-provider-system

- Goal: 实现发布 provider 抽象和发布记录
- Scope: publish jobs、API/browser fallback provider boundary
- Non-goals: phase-one 默认启用真实自动发布
- Key decisions: browser automation 作为 fallback，不作为业务层分叉
- Acceptance: publish job 可创建、状态可查询
- Risks: 真实平台风控
- Dependencies: review-workflow-and-audit

## feishu-sync

- Goal: 同步采集/生成/发布数据到飞书
- Scope: sync records、bitable mapping
- Non-goals: 飞书内部复杂协同流
- Key decisions: sync 通过 provider 隔离
- Acceptance: sync record 可创建、状态可查询
- Risks: 外部 schema 映射变化
- Dependencies: publishing-provider-system

## rest-api

- Goal: 提供稳定 REST 接口
- Scope: runs、drafts、publish-jobs、sync-records、audit-logs
- Non-goals: 外部开放平台级安全体系
- Key decisions: 所有路由复用 application services
- Acceptance: 核心主链路可通过 REST 触发和查询
- Risks: 接口膨胀
- Dependencies: architecture-foundation, pipeline-orchestration

## mcp-server

- Goal: 提供 MCP 工具能力
- Scope: tool discovery、tool call、shared use cases
- Non-goals: phase-one 完整生产级兼容
- Key decisions: 先交付轻量 JSON-RPC tool surface
- Acceptance: 至少可列出 tools 并启动 pipeline
- Risks: 与正式 MCP 客户端的兼容差异
- Dependencies: architecture-foundation, pipeline-orchestration

## web-console

- Goal: 提供内部操作台
- Scope: 启动 pipeline、查看 drafts、审核、发布、日志查看
- Non-goals: 重型 SPA
- Key decisions: server-rendered UI 优先
- Acceptance: 页面可用且主链路可演示
- Risks: 功能增长后需要拆页面
- Dependencies: architecture-foundation, review-workflow-and-audit, publishing-provider-system

## testing-observability-and-devex

- Goal: 建立测试、环境、日志和开发体验
- Scope: pytest、env example、README、observability baseline
- Non-goals: 企业级监控平台
- Key decisions: 先保证本地可运行和可验证
- Acceptance: 测试通过、README 可指导启动
- Risks: 观测能力初期较轻
- Dependencies: architecture-foundation

## portfolio-packaging

- Goal: 将项目整理成可展示的作品集交付
- Scope: showcase、demo script、project narrative
- Non-goals: 商业发布页
- Key decisions: 强调平台化与工程化能力，而不是只强调模型调用
- Acceptance: 有清晰 demo 路径和项目亮点说明
- Risks: 真实 provider 未接入时需要清楚标识 mock 边界
- Dependencies: testing-observability-and-devex, web-console, mcp-server
