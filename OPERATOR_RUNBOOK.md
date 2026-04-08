# OPERATOR_RUNBOOK

## 1. 启动

```bash
pip install -e .[dev]
pytest -q
uvicorn app.main:app --reload
```

## 2. 打开工作台

- 浏览器访问 `/`
- 如启用 auth，则先走 `/login`

## 3. 常用操作

### 一键完整链路
- 在首页输入 keywords / topic_words
- 选择 `full`
- 提交后查看最新 run 的 8 阶段状态

### 逐步执行
- 在首页选择 `step`
- 创建 staged run
- 再通过 REST / MCP / Web 逐阶段推进

### 审核与发布
- 草稿默认进入 review pending
- approve 后可执行 publish prepare / preview / send
- 默认 send 仍以 dry-run 为主

### 同步
- `sync_crawled`：同步采集内容 / 分析摘要 / 候选源数据
- `sync_generated`：同步选题 / 草稿 / 审核 / 发布结果

## 4. 故障排查

优先查看：

- `/console/providers`
- `/console/runs/{run_id}/diagnostics`
- `/api/providers/status`
- `/api/audit-logs`
- `/api/sync-records`

## 5. 安全规则

- 默认人工审核后发布
- 默认 dry-run first
- 不要绕过 publish safety gate
- 没有真实权限时，只做 fixture/mock/safe-stub 验证
