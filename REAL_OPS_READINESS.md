# REAL_OPS_READINESS

## 当前状态

项目已达到“真实外部权限之外基本完成”的状态：

- 8 阶段内容流水线、REST、MCP、Web 工作台、schema、prompt、publish/sync 语义、tests/docs 均已就位
- 默认可用 fixture/mock/safe-stub 完成整条 dry-run 演示链路
- 真实验证仅受外部登录态 / 密钥 / 权限限制

## 剩余真实验证项

### Collector
- 需要真实 XHS storage state 或 cookies
- 需要验证真实 DOM 与当前选择器/抽取逻辑

### Model
- 需要至少一个可用 OpenAI-compatible 端点
- 需要验证真实 JSON schema 输出稳定性

### Publish
- 需要真实发布权限（browser state 或 publish API token）
- 默认仍应保留人工审核 gate

### Sync
- 需要真实 `lark-cli` 登录态与目标 Base/Sheet 权限

## 推荐真实联调顺序

1. 先验证 collector login + 搜索/详情 dry-run
2. 再验证 model analyze/topic/draft/image plan
3. 再验证 publish preview / send（仅在确认权限后）
4. 最后验证 sync_crawled / sync_generated
