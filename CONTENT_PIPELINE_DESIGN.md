# CONTENT_PIPELINE_DESIGN

## 目标

在不推翻原工程骨架的前提下，把系统升级成一个“内容助手工作台”。

## 核心设计

### 统一服务层

`PipelineService` 仍然是三种入口的唯一业务中心：

- REST API
- MCP tools
- Web Console

### 8 阶段显式化

每个 run 都按如下顺序组织：

1. crawl
2. analyze
3. topic
4. draft
5. image
6. review
7. publish
8. sync

每个阶段记录：

- status
- provider
- started_at / finished_at
- input_summary
- output_summary
- error_message

### Crawl 设计

collector provider 内部采用：

1. collect_candidates
2. hydrate details
3. filter
4. persist SourcePosts

而不是在 route / UI 层拼业务逻辑。

### Publish 设计

- `prepare`：生成候选发布包
- `preview`：给 Web / REST / MCP 展示
- `send`：真正发送或 dry-run 发送

### Sync 设计

- `sync_crawled`：同步采集侧资产
- `sync_generated`：同步生成侧资产

## 持久化策略

- `WorkflowRun`：run 级状态
- `WorkflowStageEvent`：阶段级诊断
- `SourcePost / AnalysisReport / TopicSuggestion / ContentDraft / ImageAsset`
- `PublishJob`
- `SyncRun / SyncRecord`
- `AuditLog`

## 兼容策略

旧 REST 路径仍保留兼容别名，避免现有测试和集成路径断裂。
